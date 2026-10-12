#include "ble_control.hpp"
#include "protocol.hpp"
#include <string>
#include <mutex>
#include <atomic>
#include "cJSON.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
extern "C" {
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "host/util/util.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"
}
namespace otto_ble {
namespace {
// Nordic UART UUIDs; RX is newline-delimited JSON, TX is the latest request response.
const ble_uuid128_t service=BLE_UUID128_INIT(0x9e,0xca,0xdc,0x24,0x0e,0xe5,0xa9,0xe0,0x93,0xf3,0xa3,0xb5,0x01,0x00,0x40,0x6e);
const ble_uuid128_t rx=BLE_UUID128_INIT(0x9e,0xca,0xdc,0x24,0x0e,0xe5,0xa9,0xe0,0x93,0xf3,0xa3,0xb5,0x02,0x00,0x40,0x6e);
const ble_uuid128_t tx=BLE_UUID128_INIT(0x9e,0xca,0xdc,0x24,0x0e,0xe5,0xa9,0xe0,0x93,0xf3,0xa3,0xb5,0x03,0x00,0x40,0x6e);
std::string incoming, response="{}";
std::mutex response_mutex;
std::atomic<unsigned> generation{0};
struct Packet { std::string body; unsigned generation; };
QueueHandle_t queue;
uint8_t address_type;
void advertise();
int gap(ble_gap_event *event,void *) {
    if (event->type==BLE_GAP_EVENT_DISCONNECT) {
        ++generation; incoming.clear();
        auto *packet=new Packet{"",generation.load()};
        if (xQueueSend(queue,&packet,0)!=pdTRUE) delete packet;
        advertise();
    } else if (event->type==BLE_GAP_EVENT_CONNECT && event->connect.status!=0) advertise();
    else if (event->type==BLE_GAP_EVENT_ADV_COMPLETE) advertise();
    return 0;
}
int access(uint16_t,uint16_t,ble_gatt_access_ctxt *ctx,void *) {
    if (ctx->op==BLE_GATT_ACCESS_OP_READ_CHR) {
        std::lock_guard<std::mutex> lock(response_mutex);
        return os_mbuf_append(ctx->om,response.data(),response.size())==0 ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
    }
    if (ctx->op!=BLE_GATT_ACCESS_OP_WRITE_CHR) return BLE_ATT_ERR_WRITE_NOT_PERMITTED;
    const size_t len=OS_MBUF_PKTLEN(ctx->om);
    if (incoming.size()+len>65536) { incoming.clear(); return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN; }
    std::string part(len,'\0');
    if (os_mbuf_copydata(ctx->om,0,len,part.data())!=0) return BLE_ATT_ERR_UNLIKELY;
    incoming+=part;
    auto end=incoming.find('\n');
    if (end!=std::string::npos) {
        auto *packet=new Packet{incoming.substr(0,end),generation.load()};
        incoming.erase(0,end+1);
        if (xQueueSend(queue,&packet,0)!=pdTRUE) { delete packet; return BLE_ATT_ERR_INSUFFICIENT_RES; }
    }
    return 0;
}
ble_gatt_chr_def chars[3]={};
ble_gatt_svc_def services[2]={};
void advertise() {
    ble_hs_adv_fields fields={}; fields.flags=BLE_HS_ADV_F_DISC_GEN|BLE_HS_ADV_F_BREDR_UNSUP;
    fields.uuids128=const_cast<ble_uuid128_t *>(&service);fields.num_uuids128=1; fields.uuids128_is_complete=1;
    if (ble_gap_adv_set_fields(&fields)) return;
    ble_hs_adv_fields scan={}; const char *name="Otto-0E70";
    scan.name=(uint8_t *)name;scan.name_len=9;scan.name_is_complete=1;ble_gap_adv_rsp_set_fields(&scan);
    ble_gap_adv_params params={};params.conn_mode=BLE_GAP_CONN_MODE_UND;params.disc_mode=BLE_GAP_DISC_MODE_GEN;
    int rc=ble_gap_adv_start(address_type,nullptr,BLE_HS_FOREVER,&params,gap,nullptr);
    ESP_LOGI("otto_ble","advertising Otto-0E70 rc=%d",rc);
}
void sync() { if (ble_hs_util_ensure_addr(0)==0 && ble_hs_id_infer_auto(0,&address_type)==0) advertise(); }
void host(void *) { nimble_port_run(); nimble_port_freertos_deinit(); }
void worker(void *) {
    while (true) {
        Packet *packet=nullptr;
        if (xQueueReceive(queue,&packet,portMAX_DELAY)!=pdTRUE) continue;
        if (packet->generation!=generation.load()) { delete packet; continue; }
        if (packet->body.empty()) { otto_protocol::dispatch("/api/stop","{}"); delete packet; continue; }
        cJSON *root=cJSON_ParseWithLength(packet->body.data(),packet->body.size());
        cJSON *id=cJSON_GetObjectItemCaseSensitive(root,"id");
        cJSON *path=cJSON_GetObjectItemCaseSensitive(root,"path");
        cJSON *body=cJSON_GetObjectItemCaseSensitive(root,"body");
        char *payload=body ? cJSON_PrintUnformatted(body) : nullptr;
        otto_protocol::Reply reply{R"({"error":"invalid BLE envelope"})",400};
        if (cJSON_IsNumber(id) && cJSON_IsString(path)) reply=otto_protocol::dispatch(path->valuestring,payload ? payload : "{}");
        cJSON *out=cJSON_CreateObject();
        cJSON_AddNumberToObject(out,"id",cJSON_IsNumber(id)?id->valuedouble:0);
        cJSON_AddNumberToObject(out,"status",reply.status);
        cJSON_AddItemToObject(out,"result",cJSON_Parse(reply.json.c_str()));
        char *encoded=cJSON_PrintUnformatted(out);
        { std::lock_guard<std::mutex> lock(response_mutex); response=encoded ? encoded : "{}"; }
        cJSON_free(encoded); cJSON_free(payload);cJSON_Delete(out);cJSON_Delete(root);delete packet;
    }
}
}
esp_err_t start() {
    queue=xQueueCreate(4,sizeof(Packet *)); if (!queue) return ESP_ERR_NO_MEM;
    ESP_ERROR_CHECK(nimble_port_init());
    ble_hs_cfg.sync_cb=sync;
    ble_svc_gap_init();ble_svc_gatt_init();ble_svc_gap_device_name_set("Otto-0E70");
    chars[0].uuid=&rx.u;chars[0].access_cb=access;chars[0].flags=BLE_GATT_CHR_F_WRITE;
    chars[1].uuid=&tx.u;chars[1].access_cb=access;chars[1].flags=BLE_GATT_CHR_F_READ;
    services[0].type=BLE_GATT_SVC_TYPE_PRIMARY;services[0].uuid=&service.u;services[0].characteristics=chars;
    if (ble_gatts_count_cfg(services) || ble_gatts_add_svcs(services)) return ESP_FAIL;
    if (xTaskCreate(worker,"ble_commands",8192,nullptr,4,nullptr)!=pdPASS) return ESP_ERR_NO_MEM;
    nimble_port_freertos_init(host);return ESP_OK;
}
}

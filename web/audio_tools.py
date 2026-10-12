"""Find installed FFmpeg or the wheel-bundled executable."""
import shutil

def ffmpeg():
    installed = shutil.which('ffmpeg')
    if installed:
        return installed
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

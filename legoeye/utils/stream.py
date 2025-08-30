from core.stream import StreamManager
from core.record import recordManager
from core.picam import PicamManager
from utils.paths import Paths
from utils.logger import Logger
import subprocess
import time
import os
import glob
from datetime import timedelta
import threading

streamMngr = StreamManager()
picamMngr = PicamManager()
recordMngr = recordManager()
paths = Paths()
logger = Logger.get_logger(__name__)


def does_all_have_same_framerate (clips_detail_list):
    for i, clip_detail in enumerate(clips_detail_list):
        if (i == 0):
            _framerate = clip_detail['framerate']
            continue
        if(_framerate != clip_detail['framerate']):
            return False
    return True
        

def startStream(by=None):
    """Starts the video stream

    - increament the streaming count

    If encoder is not running:
    - starts the encoder
    - ***SLEEPS*** for 3 seconds to allow the camera and encoder to
      stabilize before the stream is ready for delivery.
      
    """
    logger.info(f"[startStream] Attempting to start stream {('by ' + by) if by else ''}")
    streamMngr.increamentStreamingCount()
    if not picamMngr.isEncoderRunning:
        picamMngr.startEncoder(by)
        time.sleep(3)
        logger.info(f"[startStream] streaming starts; active streams : {streamMngr.streamingCount} ; recording status : {recordMngr.isRecording}")
    else:
        logger.info(f"[startStream] streaming already active; active streams : {streamMngr.streamingCount} ; recording status : {recordMngr.isRecording}")

def stopStream(by=None):
    """Stops the video stream

    - decreament the streaming count

    If no user is accessing the stream and no recording is going on:
    - stops the encoder

    """
    logger.info(f"[stopStream] Attempting to stop stream {('by ' + by) if by else ''}")
    streamMngr.decrementStreamingCount()
    if (not streamMngr.isStreaming() and not recordMngr.isRecording):
        picamMngr.stopEncoder(by)
        logger.info(f"[stopStream] streaming ends; active streams : {streamMngr.streamingCount} ; recording status : {recordMngr.isRecording}")
    else:
        logger.info(f"[stopStream] streaming doesn't end; active streams : {streamMngr.streamingCount} ; recording status : {recordMngr.isRecording}")

def startSeparateFFmpegStreams(stream_id:str, clips_detail_list:list, start_epoc:int, end_epoc:int,precise:bool=False):
    
    segment_start_number = 0
    master_path = f'{paths.FOOTAGE_STREAM_DIR}/{stream_id}/master.m3u8'

    start_timestamp = None

    for i,clip_detail in enumerate(clips_detail_list):
        ts_files = glob.glob(f'{paths.FOOTAGE_STREAM_DIR}/{stream_id}/stream_*.ts')
        segment_start_number = len(ts_files)
        clip_path = paths.mk_full_video_path(video_id=clip_detail['id'])

        # if this is the first clip
        if(i == 0):
            
            # if the requested start time epoc lies before the first clip's start timestamp which is clip_detail['timestamp']
            if (start_epoc <= int(clip_detail['timestamp'])):
                
                # yes, then the first clip will be processed from the begining so setting the start_timestamp to None so that ss flag won't be passed to the ffmpeg
                start_timestamp = None

            # requested start time epoc lies after the first clip's start timestamp
            else:

                # no, then we need to tell ffmpeg to start from given time,
                # to calculate this given time we need the difference between the start of the clip and requested start
                diff_secs = start_epoc - int(clip_detail['timestamp'])

                td = timedelta(seconds=diff_secs)
                hours, remainder = divmod(td.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)

                # ffmpeg needs timestamp in hh:mm:ss format
                start_timestamp = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        else:

            # this is not the first clip so it will be processed from its begining, so setting the start timestamp to None
            start_timestamp = None

        # if this is the last clip (clip_detail)
        if(i == len(clips_detail_list)-1):

            # if the requested end time lies outside the last clip's time stamp,
            # it is being calculated by adding the clip_detail['timestamp'] (which is the start timestamp) and clip_detail['duration'] (which is clip's duration)
            if (end_epoc >= int(clip_detail['timestamp']) + int(clip_detail['duration'])):

                # yes, then setting duration to None so that -t flag (duration) is not added to the ffmpeg so that ffmpeg processes the clip till its end
                duration =  None

            # requested end time lies before the last clip's time stamp, so we need to tell ffmpeg to process the last clip till given duration via -t flag
            else:

                # checking if this is the first clip as well which means this is the only clip as it the last clip as well as len(clips_detail_list)-1 == 0 is True
                if( i == 0):

                    # checking if there is start_timestamp to know that if we are processing the clip from the beinging or not
                    # we need this to calculate the duration of the clip as end epoc lies before the clip's end and thus we need to pass that duration the ffmpeg
                    if start_timestamp:

                        # calculating the duration by subtracting the given start epoc time and end epoc time, as we have bounds from both the ends
                        diff_secs = end_epoc - start_epoc

                    # start_timestamp is None which means that we are processing the clip from the begining
                    else:
                    
                    # thus the duration will the given end epoc time - start timestamp of the clip (clip_detail['timestamp'])
                        diff_secs = end_epoc - int(clip_detail['timestamp'])
                
                # this is not the first clip which means there are more than one clip
                else:

                    # thus this clip will be processed from the begining,
                    # thus the duration will be this clip's start - the given end epoc time
                    diff_secs = end_epoc - int(clip_detail['timestamp'])

                td = timedelta(seconds=diff_secs)
                hours, remainder = divmod(td.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)

                duration = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        
        # this is isn't the last clip
        else:

            # thus we will need to process it till the end
            duration = None

        ffmpeg_cmd = [
            'ffmpeg',
            '-fflags' ,'+genpts',
            '-f', 'h264', '-framerate', str(clip_detail['framerate']),
            *(['-ss',str(start_timestamp)] if (not precise and start_timestamp) else []),
            '-i',clip_path,
            *(['-ss',str(start_timestamp)] if (precise and start_timestamp) else []),
            *(['-t', str(duration)] if duration else []),
            '-c:v', 'copy',
            "-vsync", "passthrough",
            '-hls_time', '6',
            '-hls_segment_filename', f'{paths.FOOTAGE_STREAM_DIR}/{stream_id}/stream_%07d.ts',
            '-hls_playlist_type', 'event',
            '-hls_flags', 'append_list+omit_endlist',
            '-hls_start_number', str(segment_start_number),
            master_path
        ]
        try :
            subprocess.run(ffmpeg_cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(            
                "FFmpeg failed for %s (exit code %d).\n"
                "stdout:\n%s\n"
                "stderr:\n%s",
                clip_detail,
                e.returncode,
                e.stdout.strip(),
                e.stderr.strip(),)
            continue
        except Exception as e:
            logger.error(f"Error occurred while streaming footage {clip_detail}; Error: {e}")
            continue

    # append the ENDLIST flag in master playlist file
    if not os.path.exists(master_path):
        logger.warn(f"Can't append #EXT-X-ENDLIST as Master playlist file of stream id : {stream_id} doesn't exist.")
    with open(master_path, 'a') as f:
        f.write('#EXT-X-ENDLIST\n')


def startConcatedFFmpegStream(stream_id:str,clips_detail_list:list, start_epoc:int, end_epoc:int, framerate:int, precise:bool=False):
    input = "concat:" + "|".join(paths.mk_full_video_path(video_id=clip_detail['id']) for clip_detail in clips_detail_list)
    logger.debug("[startConcatedFFmpegStream] Concated input: ", input)

    if (start_epoc <= int(clips_detail_list[0]['timestamp'])):
        start_timestamp = None
    else:
        diff_secs = start_epoc - int(clips_detail_list[0]['timestamp'])

        td = timedelta(seconds=diff_secs)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        start_timestamp = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    if (end_epoc >= int(clips_detail_list[-1]['timestamp'])):
        duration =  None
    else:
        if start_timestamp:
            diff_secs = end_epoc - start_epoc
        else:
            diff_secs = end_epoc - int(clips_detail_list[0]['timestamp'])

        td = timedelta(seconds=diff_secs)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        duration = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    ffmpeg_cmd = [
        'ffmpeg',
        '-fflags' ,'+genpts',
        '-f', 'h264',
        '-framerate', str(framerate),
        *(['-ss',str(start_timestamp)] if (not precise and start_timestamp) else []),
        '-i', input,
        '-c:v', 'copy',
        "-vsync", "passthrough",
        *(['-ss',str(start_timestamp)] if (precise and start_timestamp) else []),
        *(['-t', str(duration)] if duration else []),
        '-hls_time', '6',
        '-hls_segment_filename', f'{paths.FOOTAGE_STREAM_DIR}/{stream_id}/stream_%07d.ts',
        '-hls_playlist_type', 'vod',
        f'{paths.FOOTAGE_STREAM_DIR}/{stream_id}/master.m3u8'
    ]
    try :
        subprocess.run(ffmpeg_cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(            
            "FFmpeg failed for %s (exit code %d).\n"
            "stdout:\n%s\n"
            "stderr:\n%s",
            clips_detail_list,
            e.returncode,
            e.stdout.strip(),
            e.stderr.strip()
        )
    except Exception as e:
        logger.error(f"Error occurred while streaming footages {clips_detail_list}; Error: {e}")


def startFootageRangeStream(start_epoc, end_epoc, clips_detail_list:list, precise:bool=False):
    if(len(clips_detail_list) == 0): 
        logger.info("[startFootageRangeStream]  clips_detail_list is empty")
        return

    stream_id = f"{start_epoc}{end_epoc}"
    os.makedirs(f'{paths.FOOTAGE_STREAM_DIR}/{stream_id}', exist_ok=True)


    _does_all_have_same_framerate = does_all_have_same_framerate(clips_detail_list=clips_detail_list)


    if(_does_all_have_same_framerate):
        footage_stream_thread = threading.Thread(target=startConcatedFFmpegStream, kwargs={
            'stream_id':       stream_id,
            'clips_detail_list': clips_detail_list,
            'start_epoc':      start_epoc,
            'end_epoc':        end_epoc,
            'framerate':       clips_detail_list[0]['framerate'],
            'precise':         precise,
        })
    else:
        footage_stream_thread = threading.Thread(target=startConcatedFFmpegStream, kwargs={
            'stream_id': stream_id,
            'clips_detail_list': clips_detail_list,
            'start_epoc': start_epoc,
            'end_epoc': end_epoc,
            'precise': precise
        })
    footage_stream_thread.daemon = True
    footage_stream_thread.start()
    logger.info(f"[startFootageRangeStream] footage_stream_thread method initiated; StreamID: {stream_id}")

    return stream_id



    

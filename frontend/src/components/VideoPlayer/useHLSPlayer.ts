import { useEffect, useRef, RefObject } from 'react';
import Hls from 'hls.js';
import { FootageStatus } from '../videos-section';

interface HLSPlayerHook {
  hls: Hls | null;
}

export default function useHLSPlayer(
  videoRef: RefObject<HTMLVideoElement | null>,
  src: string,
  footage_status: FootageStatus
): HLSPlayerHook {
  const hlsRef = useRef<Hls | null>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let hls: Hls | null = null;

    const initPlayer = () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
      }

      const prev_footage_config = {
        autoStartLoad: true,
        maxBufferLength: 30,
        backBufferLength: 600,
        maxMaxBufferLength: 120,
        enableWorker: true,
        lowLatencyMode: true,
        startPosition: 0,
        maxBufferSize:60 * 1000 * 1000 //bytes
      }
      const live_config = {
        autoStartLoad: true,
        autoStart:true,
        liveSyncDuration: 3,
        liveMaxLatencyDuration: 4,
        maxMaxBufferLength: 120,
        backBufferLength: 600,
        enableWorker: true,
        lowLatencyMode: true,
        startPosition: -1,
        maxBufferSize:60 * 1000 * 1000 //bytes
      }
      if(footage_status == FootageStatus.live){
        hls = new Hls(live_config);
      }else{
        hls = new Hls(prev_footage_config);
      }
      
      hlsRef.current = hls;

      //as hls gets attached to video element
      hls.on(Hls.Events.MEDIA_ATTACHED, () => {

        //loads the src
        hls?.loadSource(src);
      });

      hls.on(Hls.Events.ERROR, (event, data) => {
        if (data.fatal) {
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              hls?.startLoad();
              break;
            case Hls.ErrorTypes.MEDIA_ERROR:
              hls?.recoverMediaError();
              break;
            default:
              initPlayer();
              break;
          }
        }
      });

      hls.attachMedia(video);
    };

    if (Hls.isSupported()) {
      initPlayer();
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      // Native HLS support (Safari)
      video.src = src;
    }

    return () => {
      hlsRef.current?.destroy();
    };
  }, [src, videoRef]);

  return { hls: hlsRef.current };
}
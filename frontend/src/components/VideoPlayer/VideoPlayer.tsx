import React, { useRef } from 'react';
import useHLSPlayer from './useHLSPlayer';
import { FootageStatus } from '../videos-section';

interface VideoPlayerProps {
    src: string;
    footage_status: FootageStatus
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ src , footage_status}) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // Initialize HLS player
    useHLSPlayer(videoRef, src, footage_status);


    return (
        <div className="relative w-full mx-auto">
            <div className="relative bg-black" ref={containerRef}>
                <video
                    ref={videoRef}
                    className="w-full block outline-none rounded-lg border-4"
                    controls
                    preload="auto"
                    playsInline
                />
            </div>
        </div>
    );
};

export default VideoPlayer;
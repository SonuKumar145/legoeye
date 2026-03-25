"use client";

import { ChevronDownIcon } from "lucide-react";
import { DotLoader } from "react-spinners";

import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import VideoPlayer from "@/components/VideoPlayer/VideoPlayer";
import { useEffect, useState } from "react";
import { main_url } from "./main_url";
import endpoints from "@/lib/apis/endpoints";

export enum FootageStatus {
  live = "live",
  prevFootage = "prevFootage",
}

export function VideoSection() {
  const [footageStatus, setFootageStatus] = useState<FootageStatus>(
    FootageStatus.prevFootage
  );
  const [liveReady, setLiveReady] = useState<boolean>(false);

  const [startOpen, setStartOpen] = useState(false);
  const [endOpen, setEndOpen] = useState(false);
  const [startTime, setStartTime] = useState<string>("10:30:00");
  const [endTime, setEndTime] = useState<string>("10:30:00");
  const [startDate, setStartDate] = useState<Date | undefined>(undefined);
  const [endDate, setEndDate] = useState<Date | undefined>(undefined);
  const [startEpoch, setStartEpoch] = useState<Number>();
  const [endEpoch, setEndEpoch] = useState<Number>();
  const [streamID, setStreamID] = useState<string>();

  //true when master file is ready in the server
  const [streamReady, setStreamReady] = useState<boolean>(false);

  useEffect(() => {
    if (footageStatus == FootageStatus.live) {
      fetch(endpoints.stream.live.start())
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
        })
        .then(() => {
          setLiveReady(true);
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    } else {
      setLiveReady(false);
      fetch(endpoints.stream.live.stop()).catch((error) => {
        console.error("Error:", error);
      });
    }
  }, [footageStatus]);

  useEffect(() => {
    if (startEpoch && endEpoch) {
      fetch(endpoints.stream.footage.start(), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          start_epoc: startEpoch,
          end_epoc: endEpoch,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          if (data.clips_detail.length > 0) {
            setTimeout(() => {
              setStreamID(data.streamID);
              console.log("streamID = ", streamID);
            }, 2000);
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  }, [startEpoch, endEpoch]);

  useEffect(() => {
    if (streamID) {
      const intervalId = setInterval(() => {
        fetch(endpoints.stream.footage.streamStatus(streamID))
          .then((response) => {
            if (!response.ok) {
              throw new Error("Network response was not ok");
            }
            return response.json();
          })
          .then((data) => {
            if (data.status == 'ready') {
              setStreamReady(true);
              clearInterval(intervalId);
            }
          })
          .catch((error) => {
            console.error("Error:", error);
          });
      }, 1000);

      return () => {
        clearInterval(intervalId);
      };
    }
  }, [streamID]);

  useEffect(() => {
    if (startDate && startTime) {
      // Parse time string HH:mm:ss
      const [hours, minutes, seconds] = startTime.split(":").map(Number);
      const dateTime = new Date(startDate);
      dateTime.setHours(hours, minutes, seconds, 0);
      // Get epoch in seconds
      const epochSec = Math.floor(dateTime.getTime() / 1000);
      setStartEpoch(epochSec);
      console.log("Epoch:", epochSec);
    }
  }, [startDate, startTime]);

  useEffect(() => {
    if (endDate && endTime) {
      // Parse time string HH:mm:ss
      const [hours, minutes, seconds] = endTime.split(":").map(Number);
      const dateTime = new Date(endDate);
      dateTime.setHours(hours, minutes, seconds, 0);
      // Get epoch in seconds
      const epochSec = Math.floor(dateTime.getTime() / 1000);
      setEndEpoch(epochSec);
      console.log("Epoch:", epochSec);
    }
  }, [endDate, endTime]);

  return (
    <div className="overflow-hiddens mx-5.5">
      <Tabs
        defaultValue={FootageStatus.prevFootage}
        onValueChange={(value) => {
          setFootageStatus(value as FootageStatus);
        }}
      >
        <TabsList className="w-[400px]">
          <TabsTrigger value={FootageStatus.prevFootage}>Footage</TabsTrigger>
          <TabsTrigger value={FootageStatus.live}>Live</TabsTrigger>
        </TabsList>
        <TabsContent value={FootageStatus.prevFootage} className="w-full">
          <div>
            Right now this options isn't available yet. So login the pi and access the raw video files for now!
          </div>
        </TabsContent>
        <TabsContent value={FootageStatus.live}>
          <div className="my-4 flex justify-center items-center">
            {liveReady ? (
              <VideoPlayer
                src={`${main_url}/stream/live/master`}
                footage_status={footageStatus}
              />
            ) : (
              <Skeleton className="h-[1080px] w-full rounded-lg" />
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}



// <div className="my-4 flex justify-center items-center w-full flex-col">
//   <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
//     {/* Start DateTime */}
//     <div className="p-4 border rounded-2xl shadow-sm">
//       <h3 className="text-lg font-semibold mb-4">Start</h3>
//       <div className="flex gap-4 items-end">
//         <div className="flex-1 flex flex-col gap-2">
//           <Label htmlFor="start-date" className="px-1">
//             Date
//           </Label>
//           <Popover open={startOpen} onOpenChange={setStartOpen}>
//             <PopoverTrigger asChild>
//               <Button
//                 variant="outline"
//                 id="start-date"
//                 className="w-full justify-between font-normal"
//               >
//                 {startDate
//                   ? startDate.toLocaleDateString()
//                   : "Select date"}
//                 <ChevronDownIcon />
//               </Button>
//             </PopoverTrigger>
//             <PopoverContent
//               className="w-auto overflow-hidden p-0"
//               align="start"
//             >
//               <Calendar
//                 mode="single"
//                 selected={startDate}
//                 captionLayout="dropdown"
//                 onSelect={(date) => {
//                   setStartDate(date);
//                   setStartOpen(false);
//                 }}
//               />
//             </PopoverContent>
//           </Popover>
//         </div>
//         <div className="flex-1 flex flex-col gap-2">
//           <Label htmlFor="start-time" className="px-1">
//             Time
//           </Label>
//           <Input
//             type="time"
//             id="start-time"
//             step="1"
//             value={startTime}
//             onChange={(e) => setStartTime(e.target.value)}
//             className="w-full bg-background appearance-none [&::-webkit-calendar-picker-indicator]:hidden"
//           />
//         </div>
//       </div>
//     </div>

//     {/* End DateTime */}
//     <div className="p-4 border rounded-2xl shadow-sm">
//       <h3 className="text-lg font-semibold mb-4">End</h3>
//       <div className="flex gap-4 items-end">
//         <div className="flex-1 flex flex-col gap-2">
//           <Label htmlFor="end-date" className="px-1">
//             Date
//           </Label>
//           <Popover open={endOpen} onOpenChange={setEndOpen}>
//             <PopoverTrigger asChild>
//               <Button
//                 variant="outline"
//                 id="end-date"
//                 className="w-full justify-between font-normal"
//               >
//                 {endDate
//                   ? endDate.toLocaleDateString()
//                   : "Select date"}
//                 <ChevronDownIcon />
//               </Button>
//             </PopoverTrigger>
//             <PopoverContent
//               className="w-auto overflow-hidden p-0"
//               align="start"
//             >
//               <Calendar
//                 mode="single"
//                 selected={endDate}
//                 captionLayout="dropdown"
//                 onSelect={(date) => {
//                   setEndDate(date);
//                   setEndOpen(false);
//                 }}
//               />
//             </PopoverContent>
//           </Popover>
//         </div>
//         <div className="flex-1 flex flex-col gap-2">
//           <Label htmlFor="end-time" className="px-1">
//             Time
//           </Label>
//           <Input
//             type="time"
//             id="end-time"
//             step="1"
//             value={endTime}
//             onChange={(e) => setEndTime(e.target.value)}
//             className="w-full bg-background appearance-none [&::-webkit-calendar-picker-indicator]:hidden"
//           />
//         </div>
//       </div>
//     </div>
//   </div>
//   {streamReady ? (
//     <>
//       <VideoPlayer
//         src={`${main_url}/stream/footage/${streamID}/master.m3u8`}
//         footage_status={footageStatus}
//       />
//     </>
//   ) : startEpoch && endEpoch ? (
//     <Skeleton className="h-[1080px] w-full rounded-lg" />
//   ) : null}
// </div>

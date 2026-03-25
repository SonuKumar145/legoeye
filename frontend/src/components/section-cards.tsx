"use client";
import { IconTrendingDown, IconTrendingUp } from "@tabler/icons-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useEffect, useState } from "react";
import { main_url } from "./main_url";
import endpoints from "@/lib/apis/endpoints";
import { DotLoader } from "react-spinners";

type storage_type = {
  total: number;
  used: number;
  free: number;
  usage: number;
};

type memory_type = {
  total: number;
  available: number;
  used: number;
  free: number;
  usage: number;
};

export function SectionCards() {
  const [cpuUsage, setCpuUsage] = useState<number>();
  const [cpuTemp, setCpuTemp] = useState<number>();
  const [memDetails, setMemDetails] = useState<memory_type>();
  const [storageDetails, setStorageDetails] = useState<storage_type>();
  const [totalVideos, setTotalVideos] = useState<number>();
  const [totalDuration, setTotalDuration] = useState<number>();

  const fetch_cpu = () => {
    fetch(endpoints.health.cpu_usage())
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setCpuUsage(data.usage);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  const fetch_temp = () => {
    fetch(endpoints.health.cpu_temp())
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setCpuTemp(data.temp);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  const fetch_mem_details = () => {
    fetch(endpoints.health.mem_details())
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setMemDetails(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  const fetch_storage_details = () => {
    console.log("\n\n\ngoing to fetch the storage details");
    fetch(endpoints.health.storage_details())
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setStorageDetails(data);
        console.log("storage data:\n", data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  const fetch_total_videos = () => {
    console.log("\n\n\ngoing to fetch the total videos");
    fetch(endpoints.db.total_videos())
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setTotalVideos(data.total_videos);
        console.log("t v:\n", data.total_videos);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  const fetch_total_videos_duration = () => {
    fetch(endpoints.db.total_videos_duration())
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setTotalDuration(data.total_videos_duration);
        console.log("t v d:\n", data.total_videos_duration);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  useEffect(() => {
    fetch_cpu();
    setInterval(() => {
      fetch_cpu();
    }, 3000);

    setTimeout(() => {
      fetch_temp();
      setInterval(() => {
        fetch_temp();
      }, 3000);
    }, 300);

    setTimeout(() => {
      fetch_mem_details();
      setInterval(() => {
        fetch_mem_details();
      }, 3000);
    }, 600);

    setTimeout(() => {
      fetch_storage_details();
      setInterval(() => {
        fetch_storage_details();
      }, 100000);
    }, 900);

    setTimeout(() => {
      fetch_total_videos();
      setInterval(() => {
        fetch_total_videos();
      }, 60000);
    }, 1200);

    setInterval(() => {
      fetch_total_videos_duration();
      setTimeout(() => {
        fetch_total_videos_duration();
      }, 60000);
    }, 3000);
  }, []);

  return (
    <div className="*:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      <Card className="@container/card">
        {storageDetails &&
        totalVideos != null &&
        totalVideos != undefined &&
        totalDuration != null &&
        totalDuration != undefined ? (
          <>
            <CardHeader>
              <CardDescription>Storage Left</CardDescription>
              <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                {storageDetails.free.toString()}
                <span className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl opacity-50">
                  {" "}
                  / {storageDetails.total.toString()} GB
                </span>
              </CardTitle>
            </CardHeader>
            <CardFooter className="flex-col items-start gap-1.5 text-sm">
              {/* <div className="line-clamp-1 flex gap-2 font-medium">
                approx 25 days storage left
              </div> */}
              <div className="text-muted-foreground">
                {(totalDuration / 3600).toFixed(2).toString()} hours of{" "}
                {totalVideos.toString()} videos
              </div>
            </CardFooter>
          </>
        ) : (
          <div className="flex justify-center items-center">
            <DotLoader color="#ffffff" />
          </div>
        )}
      </Card>
      <Card className="@container/card">
        {cpuTemp ? (
          <>
            <CardHeader>
              <CardDescription>CPU Temperature</CardDescription>
              <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                {cpuTemp.toString()}'C
              </CardTitle>
              {/* <CardAction>
                <Badge variant="outline">
                  <IconTrendingDown />
                  -2%
                </Badge>
              </CardAction> */}
            </CardHeader>
            {/* <CardFooter className="flex-col items-start gap-1.5 text-sm">
              <div className="line-clamp-1 flex gap-2 font-medium">
                Overall today : 61'C
              </div>
              <div className="line-clamp-1 flex gap-2 font-medium">
                Max today : 73'C
              </div>
            </CardFooter> */}
          </>
        ) : (
          <div className="flex justify-center items-center">
            <DotLoader color="#ffffff" />
          </div>
        )}
      </Card>
      <Card className="@container/card">
        {cpuUsage ? (
          <>
            <CardHeader>
              <CardDescription>CPU Load</CardDescription>
              <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                {cpuUsage.toString()}%
              </CardTitle>
              {/* <CardAction>
                <Badge variant="outline">
                  <IconTrendingUp />
                  +12.5%
                </Badge>
              </CardAction> */}
            </CardHeader>
            {/* <CardFooter className="flex-col items-start gap-1.5 text-sm">
              <div className="line-clamp-1 flex gap-2 font-medium">
                Overall today : 47%
              </div>
              <div className="line-clamp-1 flex gap-2 font-medium">
                Max today : 78%
              </div>
            </CardFooter> */}
          </>
        ) : (
          <div className="flex justify-center items-center">
            <DotLoader color="#ffffff" />
          </div>
        )}
      </Card>
      <Card className="@container/card">
        {memDetails ? (
          <>
            <CardHeader>
              <CardDescription>Memory Available</CardDescription>
              <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                {memDetails.available.toString()}
                <span className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl opacity-50">
                  {" "}
                  / 512 GB
                </span>
              </CardTitle>
              {/* <CardAction>
                <Badge variant="outline">
                  <IconTrendingUp />
                  +4.5%
                </Badge>
              </CardAction> */}
            </CardHeader>
            {/* <CardFooter className="flex-col items-start gap-1.5 text-sm">
              <div className="line-clamp-1 flex gap-2 font-medium">
                Overall today : 47%
              </div>
              <div className="line-clamp-1 flex gap-2 font-medium">
                Max today : 48%
              </div>
            </CardFooter> */}
          </>
        ) : (
          <div className="flex justify-center items-center">
            <DotLoader color="#ffffff" />
          </div>
        )}
      </Card>
    </div>
  );
}

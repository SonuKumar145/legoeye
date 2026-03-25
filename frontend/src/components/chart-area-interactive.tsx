"use client"

import * as React from "react"
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts"

import { useIsMobile } from "@/hooks/use-mobile"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui/toggle-group"
import { main_url } from "./main_url"

export const description = "Detected motion"

export type record = {
  id: string,
  timestamp: number,
  duration: number,
  framerate: number
}

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "var(--primary)",
  },
  mobile: {
    label: "Mobile",
    color: "var(--primary)",
  },
}

const chartDataConverter = (records: Array<record>) => {
  let chartData: Array<{
    HourEpoch: number,                //stores epoc of the start of the Hour
    duration_of_motion: number        //stores the duration of motion captured within from (Hour) to (Hour+60 mintues)
  }> = []
  let tempRecords = structuredClone(records)
  const milsecsInHour = 1000 * 60 * 60

  let endHourEpoch = Date.now()
  let startHourEpoch = endHourEpoch - milsecsInHour

  console.log("temp record: ", tempRecords)
  while (tempRecords.length != 0) {
    const lastRecord = tempRecords[tempRecords.length - 1]
    const endTimestampEpoch_ofLastRecord = lastRecord.timestamp + lastRecord.duration

    console.log("lastRecord: ", lastRecord)
    console.log("endTimestampEpoch_ofLastRecord: ", endTimestampEpoch_ofLastRecord)
    console.log("endHourEpoch: ", endHourEpoch)
    console.log("startHourEpoch: ", startHourEpoch)

    /**
     * assuming that tempRecords will have clips will be arranged in accending order where timestamp of the records will rise from 0th element to last element 
     * 
     * 
     * record's start epoch can't be greater or equal than endHourEpoch as it would have been poped out already
     * so record's startEpoch < endHourEpoch -> always true
     * 
     * record's start and end both might lie outside (both before startHourEpoch) that means record will be in previous hour, not in the current hour we are processing for.
     * so we need to push the startHour and duration_of_motion = 0 in chartData
     * 
     * record's start and end both might lie outside (record's before startHourEpoch and record's after endHourEpoch)
     * so we need to push the startHour and duration_of_motion = 60 in chartData where 60 represents 60 mintues
     * 
     * record's end might lie inside the Hour but start outside
     * so we need to push the startHour and duration_of_motion = record's end - startHourEpoch in chartData
     * 
     * record's start and end both might lie inside the Hour
     * so we need to push the startHour and duration_of_motion = record's duration in chartdata
     * 
     * record's start might lie inside the Hour but end outside
     * so we need to push the startHour and duration_of_motion = endHourEpoch - record's start in chartData
     * 
     * 
     * finally if record's start lies inside the Hour, at the end pop the record from tempRecords
     * 
     */


    if (endTimestampEpoch_ofLastRecord < startHourEpoch) {
      console.log("1")
      chartData.unshift({ HourEpoch: startHourEpoch, duration_of_motion: 0 });
    }
    // Case 2: record spans entire hour -> duration = full 60 minutes
    else if (lastRecord.timestamp < startHourEpoch && endTimestampEpoch_ofLastRecord >= endHourEpoch) {
      console.log("2")
      chartData.unshift({ HourEpoch: startHourEpoch, duration_of_motion: 60 });
    }
    // Case 3: record starts before hour but ends inside
    else if (lastRecord.timestamp < startHourEpoch && endTimestampEpoch_ofLastRecord < endHourEpoch) {
      console.log("3")
      const minutes = (endTimestampEpoch_ofLastRecord - startHourEpoch) / 60;
      chartData.unshift({ HourEpoch: startHourEpoch, duration_of_motion: minutes });
    }
    // Case 4: record fully inside the hour
    else if (lastRecord.timestamp >= startHourEpoch && endTimestampEpoch_ofLastRecord <= endHourEpoch) {
      console.log("4")
      chartData.unshift({ HourEpoch: startHourEpoch, duration_of_motion: lastRecord.duration });
    }
    // Case 5: record starts inside but ends after hour
    else if (lastRecord.timestamp >= startHourEpoch && lastRecord.timestamp < endHourEpoch && endTimestampEpoch_ofLastRecord > endHourEpoch) {
      console.log("5")
      const minutes = (endHourEpoch - lastRecord.timestamp) / 60;
      chartData.unshift({ HourEpoch: startHourEpoch, duration_of_motion: minutes });
    }

    // Finally, if the record's start is within this hour, remove it from tempRecords
    if (lastRecord.timestamp >= startHourEpoch) {
      console.log("6 popped")
      tempRecords.pop()
    } else {
      endHourEpoch = startHourEpoch
      startHourEpoch = startHourEpoch - milsecsInHour
    }
  }
  return chartData
}

enum lockStatus {
  'acquired' = 'acquired',
  'free' = 'free'
}

//ignores requests for simplicity
class FetchLock {
  static status: lockStatus = lockStatus.free
}

export function ChartAreaInteractive() {
  const isMobile = useIsMobile()
  const [timeRange, setTimeRange] = React.useState("90d")
  const [records, setRecords] = React.useState<Array<record>>([]);
  const [limit, _] = React.useState(10)
  const [offset, setOffset] = React.useState(0)

  React.useEffect(() => {
    if (isMobile) {
      setTimeRange("7d")
    }
  }, [isMobile])

  React.useEffect(() => {
    const fetchInterval = setInterval(() => {
      if (FetchLock.status == lockStatus.acquired) return
      else {
        FetchLock.status = lockStatus.acquired
      }
      console.log("fetching records for offset: ", offset)

      fetch(`${main_url}/records`, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          limit: limit,
          offset: offset
        })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then((data: {
          'records': Array<record>
        }) => {
          setRecords([...records, ...data.records.map((rcd) => {
            return (
              {
                ...rcd,
                'timestamp': rcd.timestamp * 1000
              }
            )
          })])
          if (data.records.length < limit) {
            clearInterval(fetchInterval)
            console.log("record interval cleared")
          } else {
            setOffset((of) => of + 1)
            FetchLock.status = lockStatus.free
          }
        })
        .catch(error => {
          console.error('Error:', error);
        });
    }, 30)
    return () => clearInterval(fetchInterval);
  }, [])




  const filteredData = chartDataConverter(records).filter((rcrd) => {
    const date = new Date(rcrd.HourEpoch)
    const referenceDate = new Date(Date.now())
    let daysToSubtract = 90
    if (timeRange === "30d") {
      daysToSubtract = 30
    } else if (timeRange === "7d") {
      daysToSubtract = 7
    }
    const startDate = new Date(referenceDate)
    startDate.setDate(startDate.getDate() - daysToSubtract)
    return date >= startDate
  })
  const safeDefaultIndex = isMobile
    ? -1
    : Math.min(10, filteredData.length - 1);
  return (
    <Card className="@container/card">
      <CardHeader>
        <CardTitle>Motion</CardTitle>
        <CardDescription>
          <span className="hidden @[540px]/card:block">
            Total for the last 3 months
          </span>
          <span className="@[540px]/card:hidden">Last 3 months</span>
        </CardDescription>
        <CardAction>
          <ToggleGroup
            type="single"
            value={timeRange}
            onValueChange={setTimeRange}
            variant="outline"
            className="hidden *:data-[slot=toggle-group-item]:!px-4 @[767px]/card:flex"
          >
            <ToggleGroupItem value="90d">Last 3 months</ToggleGroupItem>
            <ToggleGroupItem value="30d">Last 30 days</ToggleGroupItem>
            <ToggleGroupItem value="7d">Last 7 days</ToggleGroupItem>
          </ToggleGroup>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger
              className="flex w-40 **:data-[slot=select-value]:block **:data-[slot=select-value]:truncate @[767px]/card:hidden"
              size="sm"
              aria-label="Select a value"
            >
              <SelectValue placeholder="Last 3 months" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="90d" className="rounded-lg">
                Last 3 months
              </SelectItem>
              <SelectItem value="30d" className="rounded-lg">
                Last 30 days
              </SelectItem>
              <SelectItem value="7d" className="rounded-lg">
                Last 7 days
              </SelectItem>
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-[250px] w-full"
        >
          <AreaChart data={filteredData}>
            <defs>
              <linearGradient id="fillDesktop" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-desktop)"
                  stopOpacity={1.0}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-desktop)"
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="HourEpoch"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
              tickFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("en-US", {
                  hour: "numeric",
                  minute: "2-digit",
                  hour12: false
                })
              }}
            />
            <ChartTooltip
              cursor={false}
              defaultIndex={safeDefaultIndex}
              content={
                <ChartTooltipContent
                  labelFormatter={(value) => {
                    console.log("chart tool tip value: ", value)
                    return new Date(value).toLocaleDateString("en-US", {
                      hour: "numeric",
                      minute: "2-digit",
                      hour12: false
                    })
                  }}
                  indicator="dot"
                />
              }
            />

            <Area
              dataKey="duration_of_motion"
              type="natural"
              fill="url(#fillDesktop)"
              stroke="var(--color-desktop)"
              stackId="a"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

import React from "react";

// components

import LiquidGauge from "components/Gauges/LiquidGauge.js";


import { gql, useQuery } from "@apollo/client";
import {tempvar, tank_names, tank_sizes, tank_volumesID, tank_serialNumber} from "index.js"
const tank_colors = ["#a5778a", "#a7f199", "#87ad86", "#cb3f93", "#cb7460","#9300c0", "#89cff0", "#3f3252", "#9f1141", "#6de137"];

export default function HeaderStats() {
  // All Tanks
  // let tanks = ["1319", "1325", "1283", "1290", "1296", "1302", "1308", "2129"];

  // 6 tanks
  console.log(tempvar)
  
  console.log(tank_names)
  console.log(tank_sizes)
  console.log(tank_volumesID)


  
  let today = new Date().toISOString().slice(0, 10)
  today +=  "T00:00:00+00:00"
  console.log(today)
  let new_day = new Date()
  var tomorrow = new Date(new_day)
  tomorrow.setDate(tomorrow.getDate() + 1)
  tomorrow = tomorrow.toISOString().slice(0, 10) + "T00:00:00+00:00"
  console.log("tomorrow", tomorrow)
  
  const GET_TANK_DATA = gql`
    query Tank($tank: [BigInt], $date: Datetime, $end_date: Datetime) {
      getRawHistoryDataWithSampling(
        ids: $tank
        startTime: $date
        endTime: $end_date
        maxSamples: 0
      ) {
        floatvalue
        ts
      }
    }
  `;


  function TankData(tank, index, divisor, unit_symbol, title) {
    console.log(`tank: ${tank}`);
    const { loading, error, data } = useQuery(GET_TANK_DATA, {
      variables: { tank: tank, date: today, end_date: tomorrow},
      pollInterval: 1000,
    });

    if (loading) {
      console.log("we are loading");
      return null;
    }
    if (error) return `Error! ${error}`;
    var stats = data.getRawHistoryDataWithSampling
    console.log(stats);


    return (
      <div className="w-full lg:w-6/12 xl:w-4/12 px-2 pb-4" key={index}>
        <LiquidGauge
          key={index}
          tankid={tank_serialNumber[index]}
          gaugeTitle={title}
          unit = {unit_symbol}
          tank_size = {divisor}
          liquidColor = {tank_colors[index]}
          val= {data.getRawHistoryDataWithSampling[data.getRawHistoryDataWithSampling.length-1].floatvalue}
          state={data.getRawHistoryDataWithSampling[data.getRawHistoryDataWithSampling.length-1].floatvalue*100/divisor}
        />
      </div>
    );
  }


  



  return (
    <>
      {/* Header */}
      <div className="relative bg-lightBlue-200 md:pt-32 pb-32 pt-12 ">
        <div className="px-4 md:px-0 mx-auto w-full">
        <div className="flex flex-wrap ">
      {tank_volumesID.map((tank, index) => TankData(tank, index, tank_sizes[index], "L", tank_names[index]))}
            </div>
        </div>
      </div>

    </>
  );
}

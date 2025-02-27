<script setup lang="ts">
import { nextTick, ref } from "vue";
import { ScoredCar, GroupedCarsByManufacturerAndModel } from "./types";
import fetchAPI from "./api";
import SettingsForm from "./components/SettingsForm.vue";
import ListEntry from "./components/ListEntry.vue";
import LoadingMessage from "./components/LoadingMessage.vue";
import Header from "./components/Header.vue";

const loading = ref(false);
const scoredCars = ref<ScoredCar[]>([]);
const groupedCars = ref<GroupedCarsByManufacturerAndModel[]>();

const defaultWeightHP = 1;
const defaultWeightPrice = -1;
const defaultWeightMileage = -1;
const defaultWeightAge = -1;

async function handleAnalyze({
  url,
  weightHP,
  weightPrice,
  weightMileage,
  weightAge,
}: {
  url: string;
  weightHP: number;
  weightPrice: number;
  weightMileage: number;
  weightAge: number;
}) {
  loading.value = true;
  const apiData = await fetchAPI(url, weightHP, weightPrice, weightMileage, weightAge);
  scoredCars.value = apiData.scoredCars;
  groupedCars.value = apiData.groupedCars;
  await nextTick();
  loading.value = false;
}
</script>

<template>
  <Header />
  <div class="container">
    <div class="column">
      <SettingsForm
        :defaultWeightHP="defaultWeightHP"
        :defaultWeightPrice="defaultWeightPrice"
        :defaultWeightMileage="defaultWeightMileage"
        :defaultWeightAge="defaultWeightAge"
        @analyze="handleAnalyze"
      />
    </div>
    <div class="column">
      <div id="scoredCarsContainer">
        <ListEntry
          v-for="{ car } in scoredCars"
          :key="car.id"
          :title="`${car.manufacturer} ${car.model}`"
          :detailsURL="car.detailsURL"
          :imageURL="car.imageURL"
          :imageALT="`${car.manufacturer} ${car.model}`"
          :paragraphs="[
            car.description,
            `${car.price}€`,
            `EZ ${new Date(car.firstRegistration).toLocaleDateString('en-GB', { month: '2-digit', year: 'numeric' })} - ${car.mileage}km - ${
              car.horsePower
            }hp - ${car.fuelType}`,
          ]"
        />
      </div>
    </div>
    <div class="column">
      <div id="groupedCarsContainer">
        <ListEntry
          v-for="group in groupedCars"
          :key="group.manufacturer + group.model"
          :title="`${group.manufacturer} ${group.model}`"
          :paragraphs="[
            `Count: ${group.count}`,
            `Average Price: ${Math.round(group.averagePrice)}€`,
            `Average Mileage: ${Math.round(group.averageMileage)}km`,
            `Average Horsepower: ${Math.round(group.averageHorsePower)}hp`,
          ]"
        />
      </div>
    </div>
  </div>
  <LoadingMessage v-show="loading" />
</template>

<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f5f5f7;
  color: #333;
  margin: 0;
  padding: 20px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.container {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  max-width: 1200px;
}

.column {
  padding: 20px;
}
</style>

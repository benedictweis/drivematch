<script setup lang="ts">
import { nextTick, ref } from "vue";
import { ScoredCar, GroupedCarsByManufacturerAndModel } from "./types";
import fetchAPI from "./drivematchclient";
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
const defaultPreferredAge = 0;

const selectedGroupedCar = ref<GroupedCarsByManufacturerAndModel>();

async function handleAnalyze({
  url,
  weightHP,
  weightPrice,
  weightMileage,
  weightAge,
  preferredAge,
}: {
  url: string;
  weightHP: number;
  weightPrice: number;
  weightMileage: number;
  weightAge: number;
  preferredAge: number;
}) {
  let filterByManufacturer = "";
  let filterByModel = "";
  if (selectedGroupedCar.value !== undefined) {
    filterByManufacturer = selectedGroupedCar.value.manufacturer;
    filterByModel = selectedGroupedCar.value.model;
  }
  loading.value = true;
  const apiData = await fetchAPI(url, weightHP, weightPrice, weightMileage, weightAge, preferredAge, filterByManufacturer, filterByModel);
  scoredCars.value = apiData.scoredCars;
  groupedCars.value = apiData.groupedCars;
  await nextTick();
  loading.value = false;
}

function handleGroupedCarSelect(groupedCar: GroupedCarsByManufacturerAndModel) {
  console.log("handleGroupedCarSelect", groupedCar);
  if (
    selectedGroupedCar.value &&
    selectedGroupedCar.value.manufacturer === groupedCar.manufacturer &&
    selectedGroupedCar.value.model === groupedCar.model
  ) {
    selectedGroupedCar.value = undefined;
    return;
  }
  selectedGroupedCar.value = groupedCar;
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
        :defaultPreferredAge="defaultPreferredAge"
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
          :title="`${group.manufacturer} ${group.model} (${group.count})`"
          :paragraphs="[
            `Average Price: ${Math.round(group.averagePrice)}€`,
            `Average Mileage: ${Math.round(group.averageMileage)}km`,
            `Average Horsepower: ${Math.round(group.averageHorsePower)}hp`,
            `Average Age: ${Math.round(group.averageAge)} days`,
          ]"
          @click="handleGroupedCarSelect(group)"
          :selected="selectedGroupedCar && selectedGroupedCar.manufacturer === group.manufacturer && selectedGroupedCar.model === group.model"
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
</style>

<style scoped>
.container {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  max-width: 1200px;
}

.column {
  padding: 20px;
}
</style>

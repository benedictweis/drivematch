<script setup lang="ts">
import { nextTick, ref } from "vue";
import { ScoredCar, GroupedCarsByManufacturerAndModel } from "./types";
import fetchAPI from "./api";
import CarForm from "./components/CarForm.vue";

const loading = ref(false);
const scoredCars = ref<ScoredCar[]>([]);
const groupedCars = ref<GroupedCarsByManufacturerAndModel[]>();

const url = ref("");
const weightHP = ref(1);
const weightPrice = ref(-1);
const weightMileage = ref(-1);
const weightAge = ref(-1);

async function handleAnalyzeButton() {
  console.log(scoredCars.value);
  loading.value = true;
  const apiData = await fetchAPI(url.value, weightHP.value, weightPrice.value, weightMileage.value, weightAge.value);
  scoredCars.value = apiData.scoredCars;
  groupedCars.value = apiData.groupedCars;
  await nextTick();
  loading.value = false;
  console.log(scoredCars.value);
}
</script>

<template>
  <div class="container">
    <div class="column">
      <CarForm
        v-model:url="url"
        v-model:weightHP="weightHP"
        v-model:weightPrice="weightPrice"
        v-model:weightMileage="weightMileage"
        v-model:weightAge="weightAge"
        @analyze="handleAnalyzeButton"
      />
    </div>
    <div class="column">
      <div v-for="{ car } in scoredCars" :key="car.id" class="list-entry">
        <img class="car-image" :src="car.imageURL" :alt="car.manufacturer + ' ' + car.model" />
        <h3>
          <a :href="car.detailsURL">{{ car.manufacturer }} {{ car.model }}</a>
        </h3>
        <p>{{ car.description }}</p>
        <p>{{ car.price }}€</p>
        <p>
          EZ {{ new Date(car.firstRegistration).toLocaleDateString("en-GB", { month: "2-digit", year: "numeric" }) }} - {{ car.mileage }}km -
          {{ car.horsePower }}hp - {{ car.fuelType }}
        </p>
      </div>
    </div>
    <div class="column">
      <div v-for="group in groupedCars" :key="group.manufacturer + group.model" class="list-entry">
        <h3>{{ group.manufacturer }} {{ group.model }}</h3>
        <p>Count: {{ group.count }}</p>
        <p>Average Price: {{ group.averagePrice }}€</p>
        <p>Average Mileage: {{ group.averageMileage }}km</p>
        <p>Average Horsepower: {{ group.averageHorsePower }}hp</p>
      </div>
    </div>
  </div>
  <div v-show="loading" id="loadingMessage">Analyzing...</div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "App",
});
</script>

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

#loadingMessage {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  font-size: 18px;
  font-weight: 600;
}

.list-entry {
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 10px;
  margin-bottom: 10px;
  background-color: #fff;
}

.car-image {
  float: left;
  width: 150px;
  margin-right: 10px;
}
</style>

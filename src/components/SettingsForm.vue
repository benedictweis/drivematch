<script setup lang="ts">
import { defineProps, defineEmits } from "vue";

const props = defineProps({
  defaultWeightHP: Number,
  defaultWeightPrice: Number,
  defaultWeightMileage: Number,
  defaultWeightAge: Number,
});

const emits = defineEmits(["analyze"]);

function handleAnalyze(event: Event) {
  event.preventDefault();
  const form = event.target as HTMLFormElement;
  const url = (form.elements.namedItem("url") as HTMLInputElement).value;
  const weightHP = (form.elements.namedItem("horsepower") as HTMLInputElement).valueAsNumber;
  const weightPrice = (form.elements.namedItem("price") as HTMLInputElement).valueAsNumber;
  const weightMileage = (form.elements.namedItem("mileage") as HTMLInputElement).valueAsNumber;
  const weightAge = (form.elements.namedItem("age") as HTMLInputElement).valueAsNumber;

  emits("analyze", {
    url,
    weightHP,
    weightPrice,
    weightMileage,
    weightAge,
  });
}
</script>

<template>
  <form id="settingsForm" @submit="handleAnalyze">
    <label for="url">Mobile.de URL:</label>
    <input type="url" id="url" name="url" required /><br /><br />

    <label for="horsepower">Horsepower Weight:</label>
    <input type="number" id="horsepower" name="horsepower" min="-100" max="100" :value="defaultWeightHP" required /><br /><br />

    <label for="price">Price Weight:</label>
    <input type="number" id="price" name="price" min="-100" max="100" :value="defaultWeightPrice" required /><br /><br />

    <label for="mileage">Mileage Weight:</label>
    <input type="number" id="mileage" name="mileage" min="-100" max="100" :value="defaultWeightMileage" required /><br /><br />

    <label for="age">Age Weight:</label>
    <input type="number" id="age" name="age" min="-100" max="100" :value="defaultWeightAge" required /><br /><br />

    <button type="submit">Analyze</button>
  </form>
</template>

<style scoped>
form {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
}

input[type="url"],
input[type="number"] {
  width: calc(100% - 20px);
  padding: 10px;
  margin-bottom: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 16px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #007aff;
  color: #fff;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
}

button:hover {
  background-color: #005bb5;
}
</style>

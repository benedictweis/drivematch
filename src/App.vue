<script setup lang="ts">
import { ref } from "vue";
import analyzeCar from "./api";
const loading = ref(false);

async function handleAnalyzeButton() {
  loading.value = true;
  await analyzeCar();
  loading.value = false;
}
</script>

<template>
  <div class="container">
    <div class="column">
      <form id="carForm">
        <label for="url">Mobile.de URL:</label>
        <input type="url" id="url" name="url" required /><br /><br />

        <label for="horsepower">Horsepower Weight:</label>
        <input type="number" id="horsepower" name="horsepower" min="-100" max="100" value="1" required /><br /><br />

        <label for="price">Price Weight:</label>
        <input type="number" id="price" name="price" min="-100" max="100" value="-1" required /><br /><br />

        <label for="mileage">Mileage Weight:</label>
        <input type="number" id="mileage" name="mileage" min="-100" max="100" value="-1" required /><br /><br />

        <label for="age">Age Weight:</label>
        <input type="number" id="age" name="age" min="-100" max="100" value="-1" required /><br /><br />

        <button type="button" @click="handleAnalyzeButton()">Analyze</button>
      </form>
    </div>
    <div class="column scrollable">
      <div id="scoredCarsContainer"></div>
    </div>
    <div class="column scrollable">
      <div id="groupedCarsContainer"></div>
    </div>
  </div>
  <div v-if="loading" id="loadingMessage">Analyzing...</div>
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
  width: 100%;
  max-width: 1200px;
}

.column {
  padding: 20px;
}

.scrollable {
  overflow-y: auto;
}

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
  width: calc(100%-20px);
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
  width: auto;
  height: 150px;
  float: left;
  margin-right: 10px;
}
</style>

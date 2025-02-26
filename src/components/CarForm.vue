<script setup lang="ts">
import { defineProps, defineEmits } from "vue";

const props = defineProps({
  url: String,
  weightHP: Number,
  weightPrice: Number,
  weightMileage: Number,
  weightAge: Number,
});

const emits = defineEmits(["update:url", "update:weightHP", "update:weightPrice", "update:weightMileage", "update:weightAge", "analyze"]);

function updateField(field: "url" | "weightHP" | "weightPrice" | "weightMileage" | "weightAge", value: any) {
  emits(`update:${field}`, value);
}
</script>

<template>
  <form id="carForm">
    <label for="url">Mobile.de URL:</label>
    <input type="url" id="url" name="url" :value="props.url" @input="updateField('url', $event.target.value)" required /><br /><br />

    <label for="horsepower">Horsepower Weight:</label>
    <input
      type="number"
      id="horsepower"
      name="horsepower"
      min="-100"
      max="100"
      :value="props.weightHP"
      @input="updateField('weightHP', $event.target.value)"
      required
    /><br /><br />

    <label for="price">Price Weight:</label>
    <input
      type="number"
      id="price"
      name="price"
      min="-100"
      max="100"
      :value="props.weightPrice"
      @input="updateField('weightPrice', $event.target.value)"
      required
    /><br /><br />

    <label for="mileage">Mileage Weight:</label>
    <input
      type="number"
      id="mileage"
      name="mileage"
      min="-100"
      max="100"
      :value="props.weightMileage"
      @input="updateField('weightMileage', $event.target.value)"
      required
    /><br /><br />

    <label for="age">Age Weight:</label>
    <input
      type="number"
      id="age"
      name="age"
      min="-100"
      max="100"
      :value="props.weightAge"
      @input="updateField('weightAge', $event.target.value)"
      required
    /><br /><br />

    <button type="button" @click="$emit('analyze')">Analyze</button>
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

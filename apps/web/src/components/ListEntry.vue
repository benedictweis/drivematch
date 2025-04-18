<script setup lang="ts">
import { defineProps } from "vue";

const props = defineProps({
  title: String,
  detailsURL: String,
  paragraphs: Array,
  imageURL: String,
  imageALT: String,
  selected: Boolean,
});
</script>

<template>
  <a v-if="detailsURL" :href="detailsURL" :class="['list-entry', { selected }]" target="_blank" rel="noopener noreferrer">
    <img v-if="imageURL" class="car-image" :src="imageURL" :alt="imageALT" />
    <div class="text-content">
      <h3>{{ title }}</h3>
      <p v-for="(paragraph, index) in paragraphs" :key="index">{{ paragraph }}</p>
    </div>
  </a>
  <div v-else class="list-entry" :class="{ selected }">
    <img v-if="imageURL" class="car-image" :src="imageURL" :alt="imageALT" />
    <div class="text-content">
      <h3>{{ title }}</h3>
      <p v-for="(paragraph, index) in paragraphs" :key="index">{{ paragraph }}</p>
    </div>
  </div>
</template>

<style scoped>
.list-entry {
  display: flex;
  align-items: flex-start;
  border-radius: 10px;
  padding: 10px;
  margin-bottom: 10px;
  background-color: #fff;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
  cursor: pointer;
}

.list-entry:hover {
  background-color: #f0f0f0;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.car-image {
  width: 150px;
  margin-right: 10px;
}

.text-content {
  display: flex;
  flex-direction: column;
}

.list-entry h3 {
  margin: 0;
  font-size: 1.2em;
}

.list-entry p {
  margin: 5px 0;
}

.list-entry.selected {
  background-color: #4caf50;
}

.list-entry.selected:hover {
  background-color: #66bb6a;
}
</style>

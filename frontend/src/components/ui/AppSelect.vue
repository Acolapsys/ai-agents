<template>
  <div class="space-y-1">
    <label v-if="label" :for="id" class="block text-sm font-medium text-charcoal-blue">
      {{ label }}
    </label>
    <select
      :id="id"
      :value="modelValue"
      :disabled="disabled"
      class="w-full px-3 py-2 border border-sky-reflection rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-baltic-blue/50 disabled:bg-gray-100"
      @change="$emit('update:modelValue', $event.target.value)"
      v-bind="$attrs"
    >
      <option v-if="placeholder" value="" disabled selected>{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { useId } from 'vue'

defineProps({
  modelValue: [String, Number],
  label: String,
  placeholder: String,
  disabled: Boolean,
  id: { type: String, default: () => useId() },
  options: { type: Array, default: () => [] }
})

defineEmits(['update:modelValue'])
</script>
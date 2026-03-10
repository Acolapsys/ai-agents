<template>
  <div class="space-y-1">
    <label v-if="label" :for="id" class="block text-sm font-medium text-charcoal-blue">
      {{ label }}
      <span v-if="required" class="text-blaze-orange">*</span>
    </label>
    <input
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      class="w-full px-3 py-2 border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-baltic-blue/50"
      :class="[
        error ? 'border-blaze-orange' : 'border-sky-reflection',
        disabled ? 'bg-gray-100 cursor-not-allowed' : ''
      ]"
      @input="$emit('update:modelValue', $event.target.value)"
      @blur="$emit('blur')"
      v-bind="$attrs"
    />
    <p v-if="error" class="text-sm text-blaze-orange">{{ error }}</p>
  </div>
</template>

<script setup>
import { useId } from 'vue'

defineProps({
  modelValue: [String, Number],
  label: String,
  type: { type: String, default: 'text' },
  placeholder: String,
  disabled: Boolean,
  required: Boolean,
  error: String,
  id: { type: String, default: () => useId() }
})

defineEmits(['update:modelValue', 'blur'])
</script>
<template>
  <div
    class="rounded-full bg-sky-reflection flex items-center justify-center text-charcoal-blue font-medium"
    :class="sizeClasses[size]"
  >
    <img v-if="src" :src="src" :alt="alt" class="rounded-full object-cover w-full h-full" />
    <span v-else>{{ initials }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  src: String,
  alt: String,
  name: String,
  size: { type: String, default: 'md' }
})

const initials = computed(() => {
  if (!props.name) return '?'
  return props.name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const sizeClasses = {
  sm: 'w-6 h-6 text-xs',
  md: 'w-8 h-8 text-sm',
  lg: 'w-10 h-10 text-base'
}
</script>
<template>
  <span
    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
    :class="badgeClasses[variant]"
  >
    <slot />
  </span>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'success', 'warning', 'danger', 'info'].includes(v)
  }
})

const badgeClasses = {
  default: 'bg-gray-100 text-gray-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-honey-bronze/20 text-charcoal-blue',
  danger: 'bg-blaze-orange/20 text-blaze-orange',
  info: 'bg-sky-reflection text-charcoal-blue'
}
</script>
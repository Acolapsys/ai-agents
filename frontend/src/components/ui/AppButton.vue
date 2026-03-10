<template>
  <button
    class="inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
    :class="[
      variantClasses[variant],
      sizeClasses[size],
      { 'w-full': block }
    ]"
    :disabled="disabled"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'outline', 'danger'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  block: Boolean,
  disabled: Boolean
})

const variantClasses = {
  primary: 'bg-baltic-blue text-white hover:bg-charcoal-blue focus:ring-baltic-blue/50',
  secondary: 'bg-sky-reflection text-charcoal-blue hover:bg-sky-reflection/80 focus:ring-sky-reflection/50',
  outline: 'border border-baltic-blue text-baltic-blue hover:bg-baltic-blue/10 focus:ring-baltic-blue/50',
  danger: 'bg-blaze-orange text-white hover:bg-blaze-orange/80 focus:ring-blaze-orange/50'
}

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg'
}
</script>
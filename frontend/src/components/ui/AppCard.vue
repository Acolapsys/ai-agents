<template>
  <div class="bg-white rounded-lg shadow-sm border border-sky-reflection/20">
    <div v-if="$slots.header" class="px-4 py-3 border-b border-sky-reflection/10 bg-gray-50">
      <slot name="header" />
    </div>
    <div class="p-4">
      <slot />
    </div>
    <div v-if="$slots.footer" class="px-4 py-3 border-t border-sky-reflection/10 bg-gray-50">
      <slot name="footer" />
    </div>
  </div>
</template>
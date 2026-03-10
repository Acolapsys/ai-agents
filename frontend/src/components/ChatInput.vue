<template>
  <div class="flex items-end space-x-2">
    <div class="flex-1 relative">
      <textarea
        ref="textareaRef"
        v-model="localValue"
        placeholder="Введите сообщение (Ctrl+Enter для новой строки, Enter для отправки)"
        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-baltic-blue/50 focus:border-baltic-blue resize-none"
        :style="{ height: textareaHeight + 'px' }"
        @keydown="handleKeydown"
      ></textarea>
    </div>
    <AppButton
      @click="$emit('send')"
      :disabled="!modelValue.trim()"
      class="h-12"
    >
      Отправить
    </AppButton>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import AppButton from '@/components/ui/AppButton.vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'send'])

const localValue = ref(props.modelValue)
const textareaRef = ref(null)
const textareaHeight = ref(48) // начальная высота (примерно 1 строка)

// Синхронизация с внешним значением
watch(() => props.modelValue, (newVal) => {
  localValue.value = newVal
  adjustHeight()
})

watch(localValue, (newVal) => {
  emit('update:modelValue', newVal)
  adjustHeight()
})

const adjustHeight = () => {
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
      const scrollHeight = textareaRef.value.scrollHeight
      const maxHeight = 150 // максимальная высота ~7 строк
      textareaHeight.value = Math.min(scrollHeight, maxHeight)
    }
  })
}

const handleKeydown = (event) => {
  // Ctrl+Enter для новой строки
  if (event.key === 'Enter' && event.ctrlKey) {
    event.preventDefault()

    // Получаем текущее значение и позицию курсора
    const start = event.target.selectionStart
    const end = event.target.selectionEnd

    // Вставляем символ новой строки
    const newValue = localValue.value.substring(0, start) + '\n' + localValue.value.substring(end)
    localValue.value = newValue

    // Перемещаем курсор после новой строки
    nextTick(() => {
      if (textareaRef.value) {
        textareaRef.value.selectionStart = start + 1
        textareaRef.value.selectionEnd = start + 1
        adjustHeight()
      }
    })
    return
  }

  // Enter для отправки (без Ctrl)
  if (event.key === 'Enter' && !event.ctrlKey) {
    event.preventDefault()
    emit('send')
  }
}

onMounted(() => {
  adjustHeight()
})
</script>
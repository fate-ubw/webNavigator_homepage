<script setup>
import { ref } from 'vue'

const bibtex = `@article{webnavigator2026,
  title={WebNavigator: Overcoming Topological Blindness in Autonomous Web Navigation},
  author={Author1 and Author2 and Author3},
  journal={arXiv preprint arXiv:2602.XXXXX},
  year={2026}
}`

const copied = ref(false)

const copyBibtex = async () => {
  await navigator.clipboard.writeText(bibtex)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}
</script>

<template>
  <section id="citation" class="py-16 bg-white">
    <div class="max-w-5xl mx-auto px-4">
      <h2 class="section-title">Citation</h2>

      <p class="text-gray-600 mb-6">
        If you find our work useful, please consider citing:
      </p>

      <div class="relative">
        <pre class="bg-gray-900 text-gray-100 p-6 rounded-xl overflow-x-auto text-sm"><code>{{ bibtex }}</code></pre>
        
        <button 
          @click="copyBibtex"
          class="absolute top-4 right-4 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-md transition-colors flex items-center gap-2"
        >
          <span v-if="!copied">📋 Copy</span>
          <span v-else>✓ Copied!</span>
        </button>
      </div>
    </div>
  </section>
</template>

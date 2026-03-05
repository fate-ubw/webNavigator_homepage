<script setup>
const BASE_URL = import.meta.env.BASE_URL

const authors = [
  { name: 'Xuanwang Zhang', url: '#', aff: '1,2,3', mark: '*' },
  { name: 'Yuteng Han', url: '#', aff: '1,2', mark: '*' },
  { name: 'Jinnan Qi', url: '#', aff: '1,2' },
  { name: 'Mulong Xie', url: '#', aff: '3' },
  { name: 'Zhen Wu', url: '#', aff: '1,2', mark: '†' },
  { name: 'Xinyu Dai', url: '#', aff: '1,2' },
]

const links = [
  // { name: 'Paper', icon: '📄', url: '#', color: 'bg-red-500 hover:bg-red-600 text-white' },
  { name: 'arXiv', icon: '📚', url: '#', color: 'bg-orange-500 hover:bg-orange-600 text-white' },
  { name: 'Code', icon: '💻', url: '#', color: 'bg-gray-800 hover:bg-gray-900 text-white' },
  { name: 'Visualization', icon: '🎮', url: '#visualization', color: 'bg-blue-500 hover:bg-blue-600 text-white' },
]
</script>

<template>
  <section class="py-20 bg-gradient-to-b from-blue-50 to-white">
    <div class="max-w-5xl mx-auto px-4 text-center">
      <!-- arXiv Badge -->
      <div class="mb-6">
        <span class="inline-block px-4 py-1.5 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">
          arXiv Preprint
        </span>
      </div>

      <!-- Title -->
      <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6 leading-tight">
        WebNavigator: Global Web Navigation<br>
        <span class="text-blue-600">via Interaction Graph Retrieval</span>
      </h1>

      <!-- Authors -->
      <div class="mb-8">
        <p class="text-lg text-gray-700">
          <template v-for="(author, index) in authors" :key="author.name">
            <a :href="author.url" class="font-bold hover:text-blue-600 transition-colors">
              {{ author.name }}
              <sup class="text-sm align-super">{{ author.aff }}<span v-if="author.mark">{{ author.mark }}</span></sup>
            </a>
            <span v-if="index < authors.length - 1">, </span>
          </template>
        </p>
        <div class="mt-3 space-y-1 text-base text-gray-600">
          <p><sup>1</sup> National Key Laboratory for Novel Software Technology, Nanjing University, China</p>
          <p><sup>2</sup> School of Artificial Intelligence, Nanjing University, China</p>
          <p><sup>3</sup> Fellou AI</p>
          <p class="pt-1 text-ms text-gray-500"><sup>*</sup> Equal contribution. <sup>†</sup> Corresponding author.</p>
        </div>
      </div>

      <!-- Links -->
      <div class="flex flex-wrap justify-center gap-3">
        <a
          v-for="link in links"
          :key="link.name"
          :href="link.url"
          class="paper-link"
          :class="link.color"
        >
          <span>{{ link.icon }}</span>
          <span>{{ link.name }}</span>
        </a>
      </div>

      <!-- Teaser Figure -->
      <div class="mt-12">
        <img 
          :src="`${BASE_URL}fig2-v10.svg`" 
          alt="WebNavigator Trajectory Comparison"
          class="w-full mx-auto rounded-xl shadow-2xl"
        />
        <p class="mt-4 text-sm text-gray-500 max-w-3xl mx-auto">
          Trajectory comparison on a multi-site task (WebArena 760). WebNavigator achieves human-level planning via two navigate(domain, query) actions, whereas the ReAct baseline prematurely terminates due to Topological Blindness.
        </p>
      </div>
    </div>
  </section>
</template>

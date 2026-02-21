<script setup>
import HeroSection from './components/HeroSection.vue'
import AbstractSection from './components/AbstractSection.vue'
import MethodSection from './components/MethodSection.vue'
import ResultsSection from './components/ResultsSection.vue'
import VisualizationSection from './components/VisualizationSection.vue'
import CitationSection from './components/CitationSection.vue'
import FooterSection from './components/FooterSection.vue'
</script>

<template>
  <div class="min-h-screen">
    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-md z-50 border-b border-gray-200">
      <div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
        <span class="font-bold text-xl text-blue-600">WebNavigator</span>
        <div class="flex gap-6 text-sm">
          <a href="#abstract" class="text-gray-600 hover:text-blue-600 transition-colors">Abstract</a>
          <a href="#method" class="text-gray-600 hover:text-blue-600 transition-colors">Method</a>
          <a href="#results" class="text-gray-600 hover:text-blue-600 transition-colors">Results</a>
          <a href="#visualization" class="text-gray-600 hover:text-blue-600 transition-colors">Visualization</a>
          <a href="#citation" class="text-gray-600 hover:text-blue-600 transition-colors">Citation</a>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="pt-16">
      <HeroSection />
      <AbstractSection />
      <MethodSection />
      <ResultsSection />
      <VisualizationSection />
      <CitationSection />
    </main>

    <FooterSection />
  </div>
</template>

<style scoped>
</style>

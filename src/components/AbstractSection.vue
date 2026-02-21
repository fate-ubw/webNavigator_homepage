<script setup>
const abstractText = `Despite significant advances in autonomous web navigation, current methods remain far from human-level performance in complex web environments. We argue that this limitation stems from Topological Blindness, where agents are forced to explore via trial-and-error without access to the global topological structure of the environment. To overcome this limitation, we introduce WebNavigator, which reframes web navigation from probabilistic exploration into deterministic retrieval and pathfinding. WebNavigator constructs Interaction Graphs via zero-token cost heuristic exploration offline and implements a Retrieve-Reason-Teleport workflow for global navigation online. WebNavigator achieves state-of-the-art performance on WebArena and Online-Mind2Web. On WebArena multi-site tasks, WebNavigator achieves a 72.9% success rate, more than doubling the performance of enterprise-level agents. This work reveals that Topological Blindness, rather than model reasoning capabilities alone, is an underestimated bottleneck in autonomous web navigation.`

const highlights = [
  { value: '72.9%', label: 'Success Rate on Multi-site Tasks' },
  { value: '2×', label: 'Better than Enterprise Agents' },
  { value: '6', label: 'Action Space Size' },
]
</script>

<template>
  <section id="abstract" class="py-16 bg-white">
    <div class="max-w-5xl mx-auto px-4">
      <h2 class="section-title">Abstract</h2>
      
      <p class="text-lg text-gray-700 leading-relaxed mb-8">
        {{ abstractText }}
      </p>

      <!-- Key Highlights -->
      <div class="grid grid-cols-3 gap-6 mt-10">
        <div 
          v-for="item in highlights" 
          :key="item.label"
          class="text-center p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl"
        >
          <div class="text-3xl font-bold text-blue-600 mb-2">{{ item.value }}</div>
          <div class="text-sm text-gray-600">{{ item.label }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

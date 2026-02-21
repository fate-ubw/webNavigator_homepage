<script setup>
const phases = [
  {
    title: 'Phase I: Offline Interaction Graph Construction',
    icon: '🗺️',
    description: 'Before task execution, WebNavigator employs a heuristic auto-exploration engine to systematically formalize the website\'s topological structure into a directed Interaction Graph.',
    steps: [
      {
        name: 'Heuristic Auto-Exploration',
        detail: 'A BFS-based engine systematically interacts with dynamic elements to discover web states. Each node is uniquely indexed by hashing its structural components, capturing DOM structures, accessibility trees, and screenshots.',
      },
      {
        name: 'Adaptive BFS',
        detail: 'Leverages structural differencing between DOM trees to identify newly added elements, significantly reducing exploration overhead by focusing on newly emerged interactive elements.',
      },
      {
        name: 'Graph Indexing',
        detail: 'All discovered nodes are embedded using multimodal embeddings and indexed into a vector database for efficient retrieval during online navigation.',
      },
    ],
    highlight: 'Zero-token cost: No LLM involvement required, only a homepage URL as input.',
  },
  {
    title: 'Phase II: Online Retrieval-Augmented Navigation',
    icon: '🎯',
    description: 'During inference, the Global-View Navigator bridges the agent\'s intent with the environment\'s deterministic structure through a three-stage Retrieve-Reason-Teleport workflow.',
    steps: [
      {
        name: 'Retrieve',
        detail: 'Given a navigation query, retrieve top-k candidate nodes from the Interaction Graph via late-interaction multimodal retrieval, which preserves fine-grained spatial cues through token-level matching.',
      },
      {
        name: 'Reason',
        detail: 'A multimodal LLM selector analyzes visual observations to identify the optimal target node from candidates, transforming navigation from generation to verification.',
      },
      {
        name: 'Teleport',
        detail: 'Compute and execute the shortest path to the target node using graph pathfinding, transitioning the agent at zero-token cost.',
      },
    ],
    highlight: 'Single action interface: navigate(domain, query) abstracts the entire workflow.',
  },
]
</script>

<template>
  <section id="method" class="py-16 bg-gray-50">
    <div class="max-w-5xl mx-auto px-4">
      <h2 class="section-title">Method</h2>

      <!-- Problem Statement -->
      <div class="mb-10">
        <h3 class="font-semibold text-lg text-gray-900 mb-3">The Problem: Topological Blindness</h3>
        <p class="text-gray-700 leading-relaxed mb-4">
          Current web navigation agents suffer from <strong>Topological Blindness</strong> — they are forced to explore via trial-and-error without access to the global topological structure of web environments. This information deficit traps agents in reactive exploration, leading to unreliable planning, prohibitive computational costs, and premature task termination.
        </p>
        <p class="text-gray-700 leading-relaxed">
          We argue that agents, like expert human users, require a persistent "mental map" of the environment. WebNavigator reframes web navigation from <em>probabilistic exploration</em> into <em>deterministic retrieval and pathfinding</em> by constructing and leveraging <strong>Interaction Graphs</strong>.
        </p>
      </div>

      <!-- Method Figure -->
      <div class="mb-12">
        <img 
          src="/fig1-v19.svg" 
          alt="WebNavigator Overview"
          class="max-w-full mx-auto rounded-xl shadow-lg"
        />
        <p class="mt-4 text-sm text-gray-500 text-center">
          Overview of WebNavigator. WebNavigator resolves Topological Blindness via a two-phase paradigm: (1) Offline Interaction Graph Construction with zero-token cost, and (2) Online Retrieval-Augmented Navigation with Retrieve-Reason-Teleport workflow.
        </p>
      </div>

      <!-- Two Phases -->
      <div class="space-y-8">
        <div 
          v-for="phase in phases" 
          :key="phase.title"
          class="bg-white rounded-xl shadow-sm overflow-hidden"
        >
          <!-- Phase Header -->
          <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
            <h3 class="text-xl font-semibold text-white flex items-center gap-3">
              <span class="text-2xl">{{ phase.icon }}</span>
              {{ phase.title }}
            </h3>
          </div>
          
          <!-- Phase Content -->
          <div class="p-6">
            <p class="text-gray-700 mb-6">{{ phase.description }}</p>
            
            <!-- Steps -->
            <div class="space-y-4">
              <div 
                v-for="(step, idx) in phase.steps" 
                :key="step.name"
                class="flex gap-4"
              >
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-semibold text-sm">
                  {{ idx + 1 }}
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900">{{ step.name }}</h4>
                  <p class="text-gray-600 text-sm mt-1">{{ step.detail }}</p>
                </div>
              </div>
            </div>

            <!-- Highlight -->
            <div class="mt-6 p-4 bg-green-50 border-l-4 border-green-500 rounded-r-lg">
              <p class="text-green-800 text-sm font-medium">{{ phase.highlight }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Key Insight -->
      <div class="mt-10 p-6 bg-blue-50 border-l-4 border-blue-500 rounded-r-xl">
        <h3 class="font-semibold text-blue-900 mb-2">Key Insight: Capability Aggregation</h3>
        <p class="text-blue-800">
          WebNavigator encapsulates the entire Retrieve-Reason-Teleport workflow into a single unified action: 
          <code class="bg-blue-100 px-2 py-0.5 rounded text-sm">navigate(domain, query)</code>. 
          The <strong>query</strong> parameter enables the agent to focus on one navigation subgoal at a time, naturally decomposing complex tasks. 
          The <strong>domain</strong> parameter enables cross-domain planning by allowing dynamic switching between Interaction Graphs. 
          This yields the most compact action space (only 6 actions) among existing methods, reducing decision complexity and improving reliability.
        </p>
      </div>
    </div>
  </section>
</template>

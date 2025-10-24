<script setup lang="ts"></script>

<template>
  <!-- Header -->
  <header class="bg-blue-600 text-white p-4 shadow">
    <h1 class="text-xl font-semibold">My Page Header</h1>
  </header>

  <!-- Body: Sidebar + Main Content -->
  <div class="flex flex-1 overflow-hidden">

    <!-- Sidebar -->
    <aside class="w-64 bg-white shadow-md p-4 overflow-y-auto">
      <h2 class="text-lg font-semibold mb-4">Menu</h2>
      <ul class="space-y-2">
        <li>
          <button class="w-full text-left px-3 py-2 rounded hover:bg-blue-100">Item 1</button>
        </li>
        <li>
          <button class="w-full text-left px-3 py-2 rounded hover:bg-blue-100">Item 2</button>
        </li>
        <li>
          <button class="w-full text-left px-3 py-2 rounded hover:bg-blue-100">Item 3</button>
        </li>
        <li>
          <button class="w-full text-left px-3 py-2 rounded hover:bg-blue-100">Item 4</button>
        </li>
      </ul>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 p-6 overflow-y-auto">
      <h2 class="text-2xl font-bold mb-4">Main Content</h2>
      <p class="mb-2">This is where your main content will go. You can add text, images, tables, or any other elements here.</p>
      <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sit amet urna a orci elementum fermentum.</p>
    </main>

  </div>
</template>

<style scoped></style>

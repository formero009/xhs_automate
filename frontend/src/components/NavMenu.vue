<template>
  <nav class="nav-menu">
    <router-link to="/theme" class="nav-item">
      <i class="icon theme-icon"></i>
      <span>提示词生成</span>
    </router-link>
    <router-link to="/generate" class="nav-item">
      <i class="icon generate-icon"></i>
      <span>内容生成</span>
    </router-link>
    <router-link to="/publish" class="nav-item">
      <i class="icon publish-icon"></i>
      <span>笔记发布</span>
    </router-link>
    <router-link to="/workflow" class="nav-item">
      <i class="icon workflow-icon"></i>
      <span>工作流</span>
    </router-link>
    <router-link to="/agent" class="nav-item">
      <i class="icon robot-icon"></i>
      <span>自动化托管</span>
    </router-link>
    <router-link to="/users" class="nav-item">
      <i class="icon user-icon"></i>
      <span>小红书账户</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">

</script>

<style scoped>
.nav-menu {
  min-width: 150px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem 1rem;
  text-decoration: none;
  border-radius: 8px;
  color: #666;
  transition: all 0.2s ease;
  font-weight: 500;
}

.nav-item:hover {
  background-color: #f8f8f8;
  color: #ff4c68;
  transform: translateX(4px);
}

.nav-item.router-link-active {
  background-color: #fff1f1;
  color: #ff4c68;
}

.icon {
  width: 20px;
  height: 20px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.7;
}

.theme-icon {
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512"><path d="M224 96l16-32l32-16l-32-16l-16-32l-16 32l-32 16l32 16l16 32zM80 160l26.66-53.33L160 80l-53.34-26.67L80 0L53.34 53.33L0 80l53.34 26.67L80 160zm352 128l-26.66 53.33L352 368l53.34 26.67L432 448l26.66-53.33L512 368l-53.34-26.67L432 288zm70.62-193.77L417.77 9.38C411.53 3.12 403.34 0 395.15 0c-8.19 0-16.38 3.12-22.63 9.38L9.38 372.52c-12.5 12.5-12.5 32.76 0 45.25l84.85 84.85c6.25 6.25 14.44 9.37 22.62 9.37c8.19 0 16.38-3.12 22.63-9.37l363.14-363.15c12.5-12.48 12.5-32.75 0-45.24zM359.45 203.46l-50.91-50.91l86.6-86.6l50.91 50.91l-86.6 86.6z" fill="currentColor"></path></svg>');
}

.generate-icon {
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 16 16"><g fill="none"><path d="M5.465 9.83a.921.921 0 0 0 1.07-.001a.98.98 0 0 0 .341-.459l.347-1.067c.085-.252.226-.48.413-.668c.187-.187.415-.328.665-.411l1.086-.353a.923.923 0 0 0-.037-1.75l-1.069-.346a1.7 1.7 0 0 1-1.08-1.078l-.353-1.084a.917.917 0 0 0-.869-.61a.92.92 0 0 0-.875.624l-.356 1.09A1.71 1.71 0 0 1 3.7 4.775l-1.084.351a.923.923 0 0 0 .013 1.745l1.067.347a1.712 1.712 0 0 1 1.081 1.083l.352 1.08c.063.18.181.337.337.448zm5.07 4.021a.806.806 0 0 0 .464.148a.813.813 0 0 0 .759-.55l.248-.762c.053-.158.143-.303.26-.421c.118-.118.262-.207.42-.259l.772-.252a.8.8 0 0 0-.023-1.521l-.764-.249a1.076 1.076 0 0 1-.68-.678l-.252-.774a.8.8 0 0 0-1.518.011l-.247.762a1.073 1.073 0 0 1-.664.679l-.776.253a.8.8 0 0 0-.388 1.221c.099.14.239.245.4.3l.763.247c.16.053.304.143.422.261c.119.118.207.263.258.422l.253.774a.8.8 0 0 0 .292.388z" fill="currentColor"></path></g></svg>');
}

.publish-icon {
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 24 24"><path d="M5 5c0 .55.45 1 1 1h12c.55 0 1-.45 1-1s-.45-1-1-1H6c-.55 0-1 .45-1 1zm2.41 9H9v5c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-5h1.59c.89 0 1.34-1.08.71-1.71L12.71 7.7a.996.996 0 0 0-1.41 0l-4.59 4.59c-.63.63-.19 1.71.7 1.71z" fill="currentColor"></path></svg>');
}

.workflow-icon {
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 640 512"><path d="M384 320H256c-17.67 0-32 14.33-32 32v128c0 17.67 14.33 32 32 32h128c17.67 0 32-14.33 32-32V352c0-17.67-14.33-32-32-32zM192 32c0-17.67-14.33-32-32-32H32C14.33 0 0 14.33 0 32v128c0 17.67 14.33 32 32 32h95.72l73.16 128.04C211.98 300.98 232.4 288 256 288h.28L192 175.51V128h224V64H192V32zM608 0H480c-17.67 0-32 14.33-32 32v128c0 17.67 14.33 32 32 32h128c17.67 0 32-14.33 32-32V32c0-17.67-14.33-32-32-32z" fill="currentColor"></path></svg>');
}

.robot-icon {
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M256 32c17.7 0 32 14.3 32 32v32h144c26.5 0 48 21.5 48 48v192c0 26.5-21.5 48-48 48H80c-26.5 0-48-21.5-48-48V144c0-26.5 21.5-48 48-48h144V64c0-17.7 14.3-32 32-32zM64 256c0 17.7 14.3 32 32 32h32v32c0 17.7 14.3 32 32 32s32-14.3 32-32v-32h96v32c0 17.7 14.3 32 32 32s32-14.3 32-32v-32h32c17.7 0 32-14.3 32-32s-14.3-32-32-32h-32v-32c0-17.7-14.3-32-32-32s-32 14.3-32 32v32h-96v-32c0-17.7-14.3-32-32-32s-32 14.3-32 32v32H96c-17.7 0-32 14.3-32 32zM168 392c0-13.3 10.7-24 24-24h128c13.3 0 24 10.7 24 24s-10.7 24-24 24H192c-13.3 0-24-10.7-24-24z" fill="currentColor"></path></svg>');
}

.user-icon {
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M224 256c70.7 0 128-57.3 128-128S294.7 0 224 0S96 57.3 96 128s57.3 128 128 128zm-45.7 48C79.8 304 0 383.8 0 482.3C0 498.7 13.3 512 29.7 512H418.3c16.4 0 29.7-13.3 29.7-29.7C448 383.8 368.2 304 269.7 304H178.3z" fill="currentColor"></path></svg>');
}

@media (max-width: 768px) {
  .nav-menu {
    width: 100%;
    flex-direction: row;
    justify-content: space-around;
    padding: 0.5rem;
  }

  .nav-item {
    flex: 1;
    justify-content: center;
    padding: 0.5rem;
  }

  .nav-item span {
    display: none;
  }

  .nav-item:hover {
    transform: translateY(-2px);
  }
}
</style> 
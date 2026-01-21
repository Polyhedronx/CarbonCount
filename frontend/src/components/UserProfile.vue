<template>
  <div class="user-profile">
    <div class="user-info">
      <el-avatar :size="40" icon="User" />
      <div class="user-details">
        <div class="username">{{ user?.username || '用户' }}</div>
        <div class="user-role">{{ user?.role === 'admin' ? '管理员' : '普通用户' }}</div>
      </div>
    </div>
    <el-button type="text" @click="$emit('logout')" class="logout-btn">
      <el-icon><SwitchButton /></el-icon>
    </el-button>
  </div>
</template>

<script>
import { SwitchButton } from '@element-plus/icons-vue'

export default {
  name: 'UserProfile',
  components: {
    SwitchButton
  },
  props: {
    user: {
      type: Object,
      default: null
    }
  },
  emits: ['logout']
}
</script>

<style scoped>
.user-profile {
  padding: 20px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 600;
  color: #333;
}

.user-role {
  font-size: 12px;
  color: #666;
}

.logout-btn {
  color: #666;
}
</style>

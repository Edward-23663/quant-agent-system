<template>
  <div class="watched-stocks">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>⭐ 关注股票管理</span>
          <el-button size="small" type="success" @click="initHotStocks">
            初始化热门股票
          </el-button>
        </div>
      </template>

      <!-- 添加股票 -->
      <div class="add-section">
        <el-input
          v-model="newTicker"
          placeholder="输入股票代码 (如: 000001)"
          style="width: 140px; margin-right: 10px;"
          @keyup.enter="addStock"
        />
        <el-input
          v-model="newName"
          placeholder="股票名称 (可选)"
          style="width: 140px; margin-right: 10px;"
          @keyup.enter="addStock"
        />
        <el-button type="primary" @click="addStock">添加</el-button>
      </div>

      <el-divider />

      <!-- 股票列表 -->
      <el-table :data="stocks" size="small" max-height="250" style="width: 100%">
        <el-table-column prop="ticker" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="100">
          <template #default="{ row }">
            {{ row.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="80">
          <template #default="{ row }">
            <el-tag :type="row.source === 'hot' ? 'warning' : 'primary'" size="small">
              {{ row.source === 'hot' ? '热门' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="added_date" label="添加日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.added_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button 
              type="danger" 
              size="small" 
              link 
              @click="removeStock(row.ticker)"
              :disabled="row.source === 'hot'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchStocks"
          @current-change="fetchStocks"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const stocks = ref([])
const newTicker = ref('')
const newName = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const fetchStocks = async () => {
  try {
    const res = await axios.get('/api/stocks/watched')
    if (res.data.success) {
      stocks.value = res.data.data
      total.value = res.data.data.length
    }
  } catch (e) {
    console.error('获取关注股票失败', e)
  }
}

const addStock = async () => {
  if (!newTicker.value) {
    return ElMessage.warning('请输入股票代码')
  }
  
  const ticker = newTicker.value.trim().replace(/[^0-9]/g, '').padStart(6, '0')
  
  try {
    const res = await axios.post('/api/stocks/watched', {
      ticker: ticker,
      name: newName.value || null
    })
    if (res.data.success) {
      ElMessage.success('添加成功')
      newTicker.value = ''
      newName.value = ''
      fetchStocks()
    } else {
      ElMessage.error(res.data.error || '添加失败')
    }
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

const removeStock = async (ticker) => {
  try {
    await ElMessageBox.confirm('确定要删除该股票吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const res = await axios.delete(`/api/stocks/watched/${ticker}`)
    if (res.data.success) {
      ElMessage.success('删除成功')
      fetchStocks()
    } else {
      ElMessage.error(res.data.error || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const initHotStocks = async () => {
  try {
    await ElMessageBox.confirm('这将添加热门股票到关注列表，是否继续？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    const res = await axios.post('/api/stocks/watched/init-hot')
    if (res.data.success) {
      ElMessage.success(`已初始化 ${res.data.count} 只热门股票`)
      fetchStocks()
    } else {
      ElMessage.error(res.data.error || '初始化失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('初始化失败')
    }
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN')
  } catch {
    return dateStr
  }
}

onMounted(() => {
  fetchStocks()
})
</script>

<style scoped>
.watched-stocks {
  margin-bottom: 15px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
.add-section {
  display: flex;
  align-items: center;
}
.pagination {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}
</style>

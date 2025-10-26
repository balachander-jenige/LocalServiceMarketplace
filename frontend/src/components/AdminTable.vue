<template>
  <div class="admin-table-container">
    <!-- Table Header -->
    <div class="table-header" v-if="showHeader">
      <div class="table-title">
        <h3>{{ title }}</h3>
        <p v-if="description" class="table-description">{{ description }}</p>
      </div>
      <div class="table-actions" v-if="$slots.actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- Filters -->
    <div class="table-filters" v-if="$slots.filters">
      <slot name="filters"></slot>
    </div>

    <!-- Table -->
    <div class="table-wrapper">
      <table class="admin-table">
        <thead>
          <tr>
            <th v-for="column in columns" :key="column.key" :class="column.class">
              <div class="th-content">
                <span>{{ column.title }}</span>
                <button v-if="column.sortable" @click="handleSort(column.key)" class="sort-btn" :class="{ active: sortBy === column.key }">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 14L12 9L17 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in paginatedData" :key="getRowKey(row, index)" :class="getRowClass(row, index)">
            <td v-for="column in columns" :key="column.key" :class="column.class">
              <slot :name="`cell-${column.key}`" :row="row" :value="getCellValue(row, column.key)" :index="index">
                {{ getCellValue(row, column.key) }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && data.length === 0" class="table-empty">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h4>{{ emptyTitle || 'No Data Available' }}</h4>
      <p>{{ emptyDescription || 'There is no data to display at the moment.' }}</p>
    </div>

    <!-- Pagination -->
    <div class="table-pagination" v-if="showPagination && totalPages > 1">
      <div class="pagination-info">
        <span>Showing {{ startItem }}-{{ endItem }} of {{ totalItems }} items</span>
      </div>
      <div class="pagination-controls">
        <button 
          @click="goToPage(currentPage - 1)" 
          :disabled="currentPage === 1"
          class="pagination-btn"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Previous
        </button>
        
        <div class="pagination-pages">
          <button 
            v-for="page in visiblePages" 
            :key="page"
            @click="goToPage(page)"
            :class="['pagination-page', { active: page === currentPage }]"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          @click="goToPage(currentPage + 1)" 
          :disabled="currentPage === totalPages"
          class="pagination-btn"
        >
          Next
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminTable',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    columns: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    description: {
      type: String,
      default: ''
    },
    showHeader: {
      type: Boolean,
      default: true
    },
    showPagination: {
      type: Boolean,
      default: true
    },
    pageSize: {
      type: Number,
      default: 10
    },
    emptyTitle: {
      type: String,
      default: ''
    },
    emptyDescription: {
      type: String,
      default: ''
    },
    rowKey: {
      type: String,
      default: 'id'
    },
    getRowClass: {
      type: Function,
      default: () => ''
    }
  },
  data() {
    return {
      currentPage: 1,
      sortBy: '',
      sortOrder: 'asc'
    }
  },
  computed: {
    sortedData() {
      if (!this.sortBy) return this.data
      
      return [...this.data].sort((a, b) => {
        const aVal = this.getCellValue(a, this.sortBy)
        const bVal = this.getCellValue(b, this.sortBy)
        
        if (aVal < bVal) return this.sortOrder === 'asc' ? -1 : 1
        if (aVal > bVal) return this.sortOrder === 'asc' ? 1 : -1
        return 0
      })
    },
    paginatedData() {
      if (!this.showPagination) return this.sortedData
      
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.sortedData.slice(start, end)
    },
    totalItems() {
      return this.data.length
    },
    totalPages() {
      return Math.ceil(this.totalItems / this.pageSize)
    },
    startItem() {
      return (this.currentPage - 1) * this.pageSize + 1
    },
    endItem() {
      return Math.min(this.currentPage * this.pageSize, this.totalItems)
    },
    visiblePages() {
      const pages = []
      const maxVisible = 5
      let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2))
      let end = Math.min(this.totalPages, start + maxVisible - 1)
      
      if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1)
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    }
  },
  methods: {
    getCellValue(row, key) {
      return key.split('.').reduce((obj, k) => obj?.[k], row)
    },
    getRowKey(row, index) {
      return row[this.rowKey] || index
    },
    handleSort(key) {
      if (this.sortBy === key) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortBy = key
        this.sortOrder = 'asc'
      }
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    }
  }
}
</script>

<style scoped>
.admin-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Table Header */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 24px;
}

.table-title h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.table-description {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Filters */
.table-filters {
  padding: 0 24px 24px 24px;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 24px;
}

/* Table */
.table-wrapper {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.admin-table th {
  background: #f8fafc;
  color: #374151;
  font-weight: 600;
  text-align: left;
  padding: 16px 24px;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-btn {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.sort-btn:hover {
  color: #6b7280;
  background: #f3f4f6;
}

.sort-btn.active {
  color: #4f46e5;
}

.admin-table td {
  padding: 16px 24px;
  border-bottom: 1px solid #f1f5f9;
  color: #374151;
}

.admin-table tbody tr:hover {
  background: #f8fafc;
}

.admin-table tbody tr:last-child td {
  border-bottom: none;
}

/* Empty State */
.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  text-align: center;
}

.empty-icon {
  color: #cbd5e1;
  margin-bottom: 16px;
}

.table-empty h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.table-empty p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

/* Pagination */
.table-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

.pagination-info {
  color: #64748b;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-pages {
  display: flex;
  gap: 4px;
}

.pagination-page {
  width: 36px;
  height: 36px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-page:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.pagination-page.active {
  background: #4f46e5;
  border-color: #4f46e5;
  color: white;
}

/* Responsive Design */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .table-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .table-pagination {
    flex-direction: column;
    gap: 16px;
    align-items: center;
  }
  
  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .admin-table th,
  .admin-table td {
    padding: 12px 16px;
  }
}

@media (max-width: 480px) {
  .table-header,
  .table-filters,
  .table-pagination {
    padding-left: 16px;
    padding-right: 16px;
  }
  
  .admin-table th,
  .admin-table td {
    padding: 10px 12px;
    font-size: 13px;
  }
  
  .pagination-page {
    width: 32px;
    height: 32px;
    font-size: 13px;
  }
}
</style>


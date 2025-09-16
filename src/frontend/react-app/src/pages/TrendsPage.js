import React from 'react';
import { ArrowUp, ArrowDown, BarChart3 } from 'lucide-react';

const TrendsPage = ({ mockTrendData }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        {/* Popular Courses Trend */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-bold mb-4">인기 강의 트렌드</h3>
          <div className="space-y-3">
            {mockTrendData.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                    index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-orange-500' : 'bg-blue-500'
                  }`}>
                    {index + 1}
                  </div>
                  <span className="font-semibold">{item.course}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`font-semibold ${item.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                    {item.change}
                  </span>
                  {item.trend === 'up' ? 
                    <ArrowUp className="w-4 h-4 text-green-600" /> : 
                    <ArrowDown className="w-4 h-4 text-red-600" />
                  }
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Search Trends */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-bold mb-4">검색 트렌드</h3>
          <div className="space-y-3">
            {[
              { keyword: '노팀플', count: 1247, change: '+23%' },
              { keyword: '성적잘줌', count: 892, change: '+15%' },
              { keyword: '재밌음', count: 673, change: '+8%' },
              { keyword: '쉬움', count: 445, change: '-3%' }
            ].map((trend, index) => (
              <div key={index} className="flex items-center justify-between">
                <div>
                  <span className="font-semibold">{trend.keyword}</span>
                  <span className="text-sm text-gray-500 ml-2">{trend.count}회</span>
                </div>
                <span className={`text-sm font-semibold ${trend.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                  {trend.change}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Weekly Activity Chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold mb-4">주간 활동 분석</h3>
        <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
          <div className="text-center text-gray-500">
            <BarChart3 className="w-12 h-12 mx-auto mb-2" />
            <p>차트 데이터 로딩 중...</p>
          </div>
        </div>
      </div>

      {/* Department Analysis */}
      <div className="grid grid-cols-3 gap-6">
        {[
          { dept: '소프트웨어학과', rating: 4.2, courses: 67 },
          { dept: '컴퓨터공학과', rating: 3.9, courses: 89 },
          { dept: 'AI학과', rating: 4.4, courses: 34 }
        ].map((dept, index) => (
          <div key={index} className="bg-white rounded-xl border border-gray-200 p-6">
            <h4 className="font-bold mb-2">{dept.dept}</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">평균 평점</span>
                <span className="font-semibold">{dept.rating}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">강의 수</span>
                <span className="font-semibold">{dept.courses}개</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrendsPage;

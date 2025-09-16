import React from 'react';
import { ArrowUp, ArrowDown, TrendingUp } from 'lucide-react';

const TrendsPage = ({ mockTrendData }) => {
  return (
    <div className="h-[calc(100vh-200px)] flex flex-col">
      {/* Trends Header */}
      <div className="bg-white border-b border-slate-200 p-4 rounded-t-xl">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-sky-100 rounded-lg">
            <TrendingUp className="w-6 h-6 text-sky-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-800">트렌드 분석</h2>
            <p className="text-sm text-slate-500">궁금한 강의 정보를 자연어로 물어보세요</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 bg-slate-50 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          {/* Popular Courses Trend */}
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">인기 강의 순위</h3>
            <div className="space-y-2">
              {mockTrendData.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors">
                  <div className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                    index === 0 ? 'bg-sky-600' : 
                    index === 1 ? 'bg-sky-500' : 
                    index === 2 ? 'bg-sky-400' : 'bg-slate-400'
                  }`}>
                      {index + 1}
                    </div>
                    <span className="font-medium text-slate-800">{item.course}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className={`font-semibold text-sm ${item.trend === 'up' ? 'text-emerald-600' : 'text-red-500'}`}>
                      {item.change}
                    </span>
                    {item.trend === 'up' ? 
                      <ArrowUp className="w-4 h-4 text-emerald-600" /> : 
                      <ArrowDown className="w-4 h-4 text-red-500" />
                    }
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Search Trends */}
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">검색 키워드 순위</h3>
            <div className="space-y-2">
              {[
                { keyword: '노팀플', count: 1247, change: '+23%' },
                { keyword: '성적잘줌', count: 892, change: '+15%' },
                { keyword: '재밌음', count: 673, change: '+8%' },
                { keyword: '쉬움', count: 445, change: '-3%' }
              ].map((trend, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors">
                  <div>
                    <span className="font-medium text-slate-800">{trend.keyword}</span>
                    <span className="text-sm text-slate-500 ml-2">{trend.count}회</span>
                  </div>
                  <span className={`text-sm font-semibold ${trend.change.startsWith('+') ? 'text-emerald-600' : 'text-red-500'}`}>
                    {trend.change}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Department Analysis */}
        <div className="grid grid-cols-3 gap-4">
        {[
          { dept: '소프트웨어학과', rating: 4.2, courses: 67, color: 'sky' },
          { dept: '컴퓨터공학과', rating: 3.9, courses: 89, color: 'slate' },
          { dept: 'AI학과', rating: 4.4, courses: 34, color: 'slate' }
        ].map((dept, index) => (
            <div key={index} className="bg-white rounded-lg border border-slate-200 p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className={`w-3 h-3 rounded-full bg-${dept.color}-500`}></div>
                <h4 className="font-semibold text-slate-800">{dept.dept}</h4>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">평균 평점</span>
                  <span className="font-semibold text-slate-800">{dept.rating}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">강의 수</span>
                  <span className="font-semibold text-slate-800">{dept.courses}개</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div 
                    className={`bg-${dept.color}-500 h-2 rounded-full transition-all duration-300`}
                    style={{width: `${(dept.rating / 5) * 100}%`}}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Insights */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <h3 className="font-semibold text-slate-800 mb-3">주요 인사이트</h3>
          <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
            <h4 className="font-medium text-slate-800 mb-2">이번 주 하이라이트</h4>
            <ul className="text-sm text-slate-700 space-y-1">
              <li>• 웹프로그래밍 강의 검색량 15% 증가</li>
              <li>• AI 관련 강의 관심도 급상승</li>
              <li>• 실습 위주 강의 선호도 증가</li>
            </ul>
          </div>
          <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
            <h4 className="font-medium text-slate-800 mb-2">추천 동향</h4>
            <ul className="text-sm text-slate-700 space-y-1">
              <li>• 노팀플 강의 검색 23% 증가</li>
              <li>• 성적 관대한 교수님 관심도 상승</li>
              <li>• 온라인 강의 선호도 감소</li>
            </ul>
          </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrendsPage;
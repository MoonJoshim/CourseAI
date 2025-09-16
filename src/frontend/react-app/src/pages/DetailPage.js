import React from 'react';
import { 
  Star, Heart, User, BookOpen, GraduationCap, Clock, Share2, Brain,
  MessageSquare, ThumbsUp
} from 'lucide-react';

const DetailPage = ({ selectedCourse, mockCourses }) => {
  const course = selectedCourse || mockCourses[0];
  
  return (
    <div className="space-y-6">
      {/* Course Header */}
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <div className="flex justify-between items-start mb-6">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <h1 className="text-3xl font-bold text-gray-900">{course.name}</h1>
              <span className="text-lg text-gray-500">({course.courseCode})</span>
              <button className="p-2 text-red-500 hover:bg-red-50 rounded-full">
                <Heart className="w-6 h-6 fill-current" />
              </button>
            </div>
            <div className="flex items-center gap-4 text-gray-600 mb-4">
              <span className="flex items-center gap-1">
                <User className="w-4 h-4" />
                {course.professor}
              </span>
              <span className="flex items-center gap-1">
                <BookOpen className="w-4 h-4" />
                {course.department}
              </span>
              <span className="flex items-center gap-1">
                <GraduationCap className="w-4 h-4" />
                {course.credits}학점
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {course.timeSlot}
              </span>
            </div>
            <p className="text-gray-500">{course.room} • {course.semester}</p>
          </div>
          
          <div className="text-right">
            <div className="flex items-center gap-2 mb-2">
              <Star className="w-6 h-6 text-yellow-500 fill-current" />
              <span className="text-2xl font-bold">{course.rating}</span>
              <span className="text-gray-500">/ 5.0</span>
            </div>
            <p className="text-sm text-gray-500">{course.reviewCount}개의 강의평</p>
            <div className="flex gap-2 mt-4">
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                강의평 작성
              </button>
              <button className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50">
                <Share2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-5 gap-6 pt-6 border-t border-gray-100">
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-1">전체 평점</p>
            <p className="text-2xl font-bold text-blue-600">{course.rating}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-1">만족도</p>
            <p className="text-2xl font-bold text-green-600">{course.sentiment}%</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-1">난이도</p>
            <p className="text-2xl font-bold text-orange-600">{course.difficulty}/5</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-1">과제량</p>
            <p className="text-2xl font-bold text-red-600">{course.workload}/5</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-1">성적</p>
            <p className="text-2xl font-bold text-purple-600">{course.gradeGenerosity}/5</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="col-span-2 space-y-6">
          {/* AI Summary */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-bold">AI 종합 분석</h3>
              <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">GPT-4 분석</span>
            </div>
            
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 mb-4">
              <p className="text-gray-800 leading-relaxed">
                {course.aiSummary} 대부분의 학생들이 적절한 난이도와 실용적인 내용에 만족하고 있으며, 
                특히 실무 경험이 풍부한 교수님의 강의 방식을 높이 평가합니다. 
                다만 과제량이 다소 많은 편이므로 시간 관리에 신경 쓰시기 바랍니다.
              </p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-green-50 rounded-lg p-3">
                <h4 className="font-semibold text-green-800 mb-2">👍 장점</h4>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• 실무 중심의 실용적 내용</li>
                  <li>• 교수님의 풍부한 경험</li>
                  <li>• 포트폴리오 제작 지원</li>
                </ul>
              </div>
              <div className="bg-orange-50 rounded-lg p-3">
                <h4 className="font-semibold text-orange-800 mb-2">⚠️ 주의사항</h4>
                <ul className="text-sm text-orange-700 space-y-1">
                  <li>• 과제량이 다소 많음</li>
                  <li>• 출석 체크 엄격</li>
                  <li>• 기초 지식 필요</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Course QA */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-bold">강의 Q&A</h3>
            </div>
            
            <div className="mb-4">
              <input
                type="text"
                placeholder="이 강의에 대해 궁금한 점을 물어보세요 (예: 팀 프로젝트는 어떤 식으로 진행돼?)"
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                AI에게 질문하기
              </button>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="font-semibold text-gray-800 mb-2">Q: 이 강의에서 팀 프로젝트는 어떤 식으로 진행되나요?</p>
                <p className="text-gray-600 text-sm mb-2">
                  A: 분석 결과, 이 강의는 개인 프로젝트 위주로 진행되며 팀 프로젝트는 없습니다. 
                  대신 중간, 기말에 개인별로 웹사이트를 제작하는 과제가 있습니다.
                </p>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>AI 답변</span>
                  <span>•</span>
                  <span>신뢰도 92%</span>
                  <span>•</span>
                  <span>15개 후기 분석</span>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="font-semibold text-gray-800 mb-2">Q: 출석은 어떻게 체크하나요?</p>
                <p className="text-gray-600 text-sm mb-2">
                  A: 매 수업마다 출석체크를 하며, 3회 이상 결석 시 F 처리됩니다. 
                  다만 사전에 연락하면 어느 정도 융통성 있게 처리해주시는 편입니다.
                </p>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>AI 답변</span>
                  <span>•</span>
                  <span>신뢰도 88%</span>
                  <span>•</span>
                  <span>23개 후기 분석</span>
                </div>
              </div>
            </div>
          </div>

          {/* Reviews */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold">강의평 ({course.reviewCount})</h3>
              <select className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
                <option>최신순</option>
                <option>평점 높은 순</option>
                <option>도움된 순</option>
              </select>
            </div>

            <div className="space-y-4">
              {[
                {
                  rating: 5,
                  semester: '2024-1',
                  content: '정말 좋은 강의였습니다. 교수님이 실무 경험이 많아서 실제로 도움되는 내용들을 많이 알려주셨어요. 과제는 좀 많지만 포트폴리오 만드는데 도움됩니다.',
                  helpful: 12,
                  date: '2024.06.15'
                },
                {
                  rating: 4,
                  semester: '2024-1', 
                  content: '내용은 좋은데 과제량이 너무 많아요. 매주 과제가 있어서 다른 과목 공부할 시간이 부족했습니다. 하지만 실력은 많이 늘었어요.',
                  helpful: 8,
                  date: '2024.06.12'
                },
                {
                  rating: 5,
                  semester: '2023-2',
                  content: '팀플이 없어서 좋았고, 개인 프로젝트도 자유도가 높아서 재밌었습니다. 성적도 노력한 만큼 잘 주시는 편이에요.',
                  helpful: 15,
                  date: '2024.01.20'
                }
              ].map((review, index) => (
                <div key={index} className="border-b border-gray-100 pb-4 last:border-b-0">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className={`w-4 h-4 ${i < review.rating ? 'text-yellow-500 fill-current' : 'text-gray-300'}`} />
                      ))}
                    </div>
                    <span className="text-sm text-gray-500">{review.semester} 수강</span>
                    <span className="text-sm text-gray-400">•</span>
                    <span className="text-sm text-gray-500">{review.date}</span>
                  </div>
                  <p className="text-gray-700 mb-3 leading-relaxed">{review.content}</p>
                  <div className="flex items-center gap-4 text-sm">
                    <button className="flex items-center gap-1 text-gray-500 hover:text-blue-600">
                      <ThumbsUp className="w-4 h-4" />
                      도움됨 {review.helpful}
                    </button>
                    <button className="text-gray-500 hover:text-blue-600">답글</button>
                    <button className="text-gray-500 hover:text-red-600">신고</button>
                  </div>
                </div>
              ))}
            </div>

            <button className="w-full mt-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600">
              더 많은 강의평 보기
            </button>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Keywords & WordCloud */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">키워드 분석</h3>
            <div className="mb-4">
              <div className="flex flex-wrap gap-2">
                {course.keywords.map((keyword, index) => (
                  <span 
                    key={index} 
                    className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                    style={{fontSize: `${Math.random() * 0.4 + 0.8}rem`}}
                  >
                    {keyword}
                  </span>
                ))}
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-lg">실습</span>
                <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-base">웹개발</span>
                <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm">JavaScript</span>
              </div>
            </div>
            <p className="text-sm text-gray-600">
              이 강의에서 가장 많이 언급되는 키워드들입니다.
            </p>
          </div>

          {/* Professor Analysis */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">교수님 분석</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">강의력</span>
                  <span className="text-sm font-semibold">4.3/5</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{width: '86%'}}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">학생 소통</span>
                  <span className="text-sm font-semibold">4.1/5</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{width: '82%'}}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">성적 관대함</span>
                  <span className="text-sm font-semibold">3.8/5</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{width: '76%'}}></div>
                </div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-700">
                같은 교수님의 다른 강의 2개도 높은 평점을 받고 있습니다.
              </p>
            </div>
          </div>

          {/* Related Courses */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">연관 강의</h3>
            <div className="space-y-3">
              {[
                { name: '고급웹프로그래밍', rating: 4.1, professor: '박교수' },
                { name: 'React개발', rating: 4.4, professor: '최교수' },
                { name: '웹서비스개발', rating: 3.9, professor: '김교수' }
              ].map((related, index) => (
                <div key={index} className="flex items-center justify-between p-3 border border-gray-100 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div>
                    <p className="font-semibold text-sm">{related.name}</p>
                    <p className="text-xs text-gray-500">{related.professor}</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star className="w-3 h-3 text-yellow-500 fill-current" />
                    <span className="text-sm font-semibold">{related.rating}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DetailPage;

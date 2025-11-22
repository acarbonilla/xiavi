import Link from 'next/link';
import { MessageCircle, Brain, TrendingUp, Mic, ArrowRight, Sparkles } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <MessageCircle className="w-8 h-8 text-primary-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
                XiAv Speech AI
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login" className="text-gray-700 hover:text-primary-600 font-medium transition-colors">
                Login
              </Link>
              <Link href="/register" className="btn-primary">
                Start Learning
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <div className="inline-flex items-center space-x-2 bg-primary-100 px-4 py-2 rounded-full mb-6 animate-fade-in">
            <Sparkles className="w-4 h-4 text-primary-600" />
            <span className="text-sm font-semibold text-primary-700">AI-Powered Speech Learning</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 animate-fade-in">
            Improve Your Speech
            <span className="block bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
              Through Conversation
            </span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto animate-slide-up">
            Practice speaking with AI on any topic. Get instant feedback, improve your communication skills,
            and track your progress—all powered by cutting-edge speech recognition and AI technology.
          </p>
          <div className="flex justify-center space-x-4 animate-slide-up">
            <Link href="/register" className="btn-primary text-lg px-8 py-3 flex items-center space-x-2">
              <span>Start Free</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href="/login" className="btn-outline text-lg px-8 py-3">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          How It Works
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="card group hover:scale-105 transition-transform duration-200">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary-200 transition-colors">
              <MessageCircle className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Choose a Topic
            </h3>
            <p className="text-gray-600">
              Select from various conversation topics—casual chat, business, academic discussions, and more.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="card group hover:scale-105 transition-transform duration-200">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-purple-200 transition-colors">
              <Mic className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Have a Conversation
            </h3>
            <p className="text-gray-600">
              Speak naturally with AI. Your speech is transcribed in real-time and AI responds contextually.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="card group hover:scale-105 transition-transform duration-200">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-green-200 transition-colors">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Get Feedback
            </h3>
            <p className="text-gray-600">
              Receive detailed analysis on clarity, fluency, vocabulary, and more. Track your improvement over time.
            </p>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                Master Communication Skills
              </h2>
              <div className="space-y-4">
                {[
                  { icon: Brain, title: 'AI-Powered Analysis', desc: 'Get intelligent feedback on your speaking patterns' },
                  { icon: TrendingUp, title: 'Track Progress', desc: 'Monitor your improvement with detailed metrics' },
                  { icon: MessageCircle, title: 'Natural Conversations', desc: 'Practice with realistic, flowing dialogue' },
                  { icon: Sparkles, title: 'Personalized Learning', desc: 'Adapt to your level and learning goals' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{item.title}</h3>
                      <p className="text-gray-600 text-sm">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-gradient-to-br from-primary-500 to-purple-500 rounded-2xl p-8 text-white">
              <h3 className="text-2xl font-bold mb-4">6 Key Metrics</h3>
              <div className="grid grid-cols-2 gap-4">
                {['Clarity', 'Fluency', 'Vocabulary', 'Grammar', 'Confidence', 'Engagement'].map((metric, idx) => (
                  <div key={idx} className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
                    <p className="font-semibold">{metric}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-primary-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Improve Your Speaking Skills?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join learners worldwide using AI to master communication
          </p>
          <Link href="/register" className="inline-flex items-center space-x-2 bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
            <span>Get Started Free</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <MessageCircle className="w-6 h-6" />
              <span className="text-xl font-bold">XiAv Speech AI</span>
            </div>
            <p className="text-gray-400">
              © 2025 XiAv Speech AI. Improve through conversation.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

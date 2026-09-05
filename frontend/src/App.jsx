import { useState } from 'react'
import Header from './components/Header.jsx'
import Hero from './components/Hero.jsx'
import DemoExplorer from './components/DemoExplorer.jsx'
import HowItWorks from './components/HowItWorks.jsx'
import RequestForm from './components/RequestForm.jsx'
import Footer from './components/Footer.jsx'
import Login from './components/Login.jsx'
import DisplayListAOI from './components/DisplayListAOI.jsx'
import { useAuth } from './context/AuthContext.jsx'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('hero')
  const { isAuthenticated } = useAuth()

  return (
    <div className="app">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      <main>
        {activeTab === 'hero' && <Hero />}
        {activeTab === 'demos' && <DemoExplorer />}
        {activeTab === 'how-it-works' && <HowItWorks />}
        {activeTab === 'request' && <RequestForm setActiveTab={setActiveTab} />}
        {activeTab === 'login' && (isAuthenticated ? <DisplayListAOI /> : <Login />)}
      </main>
      <Footer />
    </div>
  )
}

export default App
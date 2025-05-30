import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import ProductTourRetro from '../../components/onboarding/ProductTourRetro';

const OnboardingDemoRetro: React.FC = () => {
  const [isTourEnabled, setIsTourEnabled] = useState(false);
  const [userType, setUserType] = useState<'individual' | 'team' | 'enterprise'>('individual');
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const startTour = () => {
    console.log('🕹️ Starting RETRO AIOS v2 Product Tour!');
    console.log('User type:', userType);
    setIsTourEnabled(true);
  };

  const stopTour = () => {
    console.log('⏹️ Stopping RETRO AIOS v2 Product Tour');
    setIsTourEnabled(false);
  };

  return (
    <>
      <Head>
        <title>BLUELABEL AIOS - RETRO INTERFACE</title>
        <meta name="description" content="Classic AIOS retro interface experience" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet" />
      </Head>

      <div className="retro-aios-container">
        {/* Header with 3D ASCII Title */}
        <header className="retro-header">
          <div className="ascii-title">
            <pre className="title-3d">
{`██████╗ ██╗     ██╗   ██╗███████╗██╗      █████╗ ██████╗ ███████╗██╗         █████╗ ██╗ ██████╗ ███████╗
██╔══██╗██║     ██║   ██║██╔════╝██║     ██╔══██╗██╔══██╗██╔════╝██║        ██╔══██╗██║██╔═══██╗██╔════╝
██████╔╝██║     ██║   ██║█████╗  ██║     ███████║██████╔╝█████╗  ██║        ███████║██║██║   ██║███████╗
██╔══██╗██║     ██║   ██║██╔══╝  ██║     ██╔══██║██╔══██╗██╔══╝  ██║        ██╔══██║██║██║   ██║╚════██║
██████╔╝███████╗╚██████╔╝███████╗███████╗██║  ██║██████╔╝███████╗███████╗    ██║  ██║██║╚██████╔╝███████║
╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝    ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚══════╝`}
            </pre>
          </div>
          
          <div className="boot-message">
            AIOS v2 BOOTED. AWAITING INPUT.
          </div>

          {/* Navigation Menu */}
          <nav className="retro-nav">
            <span className="nav-item active">[DASHBOARD]</span>
            <span className="nav-item">[INBOX]</span>
            <span className="nav-item">[KNOWLEDGE]</span>
            <span className="nav-item">[AGENTS]</span>
            <span className="nav-item">[TERMINAL]</span>
            <span className="nav-item">[LOGS]</span>
            <span className="nav-item">[SETTINGS]</span>
          </nav>

          {/* Rainbow Progress Bar */}
          <div className="rainbow-bar"></div>
        </header>

        {/* System Dashboard Title */}
        <div className="system-dashboard">
          <h1 className="dashboard-title">System Dashboard</h1>
        </div>

        {/* Main Content Grid */}
        <div className="retro-grid">
          {/* System Status Panel */}
          <div className="system-status retro-panel">
            <div className="panel-header">SYSTEM STATUS</div>
            <div className="panel-content">
              <div className="status-line">
                <span className="status-label">CONTENT MIND</span>
                <span className="status-indicator ok">[OK]</span>
              </div>
              <div className="status-line">
                <span className="status-label">EMAIL GATEWAY</span>
                <span className="status-indicator ok">[OK]</span>
              </div>
              <div className="status-line">
                <span className="status-label">MODEL ROUTER</span>
                <span className="status-indicator ok">[OK]</span>
              </div>
              <div className="status-line">
                <span className="status-label">REDIS</span>
                <span className="status-indicator ok">[OK]</span>
              </div>
            </div>
          </div>

          {/* Agent Status Panel */}
          <div className="agent-status retro-panel">
            <div className="panel-header">AGENT STATUS</div>
            <div className="panel-content">
              <div className="agent-line">
                <span className="agent-name">ContentMind</span>
                <span className="agent-indicator ready">● READY</span>
              </div>
              <div className="agent-line">
                <span className="agent-name">ContextMind</span>
                <span className="agent-indicator processing">● PROCESSING</span>
              </div>
              <div className="agent-line">
                <span className="agent-name">DigestAgent</span>
                <span className="agent-indicator ready">● READY</span>
              </div>
              
              <div className="performance-section">
                <div className="perf-title">Performance</div>
                <div className="perf-line">
                  <span>Avg Response:</span>
                  <span className="perf-value">240ms</span>
                </div>
                <div className="perf-line">
                  <span>Tasks Today:</span>
                  <span className="perf-value">127</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions Panel */}
          <div className="quick-actions retro-panel full-width">
            <div className="panel-header">QUICK ACTIONS</div>
            <div className="panel-content">
              <div className="action-buttons">
                <button className="action-btn run-agent">RUN AGENT</button>
                <button className="action-btn upload-file upload-file-btn" onClick={startTour}>UPLOAD FILE</button>
                <button className="action-btn view-logs">VIEW LOGS</button>
                <button className="action-btn open-terminal">OPEN TERMINAL</button>
              </div>
            </div>
          </div>

          {/* Command History Panel */}
          <div className="command-history retro-panel full-width">
            <div className="panel-header">COMMAND HISTORY</div>
            <div className="panel-content">
              <div className="command-line">
                <span className="prompt">&gt;</span>
                <span className="command">process email --from john@example.com</span>
              </div>
              <div className="command-result completed">
                [COMPLETED] Q3 Report analyzed and stored
              </div>
              
              <div className="command-line">
                <span className="prompt">&gt;</span>
                <span className="command">run agent ContentMind --mode summarize</span>
              </div>
              <div className="command-result processing">
                [PROCESSING] Generating summary...
              </div>
              
              <div className="command-line">
                <span className="prompt">&gt;</span>
                <span className="command">fetch knowledge --tag "quarterly-report"</span>
              </div>
              <div className="command-result completed">
                [COMPLETED] Found 12 matching items
              </div>
              
              <div className="command-line">
                <span className="prompt">&gt;</span>
                <span className="command">check inbox --filter unread</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tour Controls */}
        <div className="tour-controls">
          <select 
            value={userType} 
            onChange={(e) => setUserType(e.target.value as any)}
            className="retro-select"
          >
            <option value="individual">INDIVIDUAL</option>
            <option value="team">TEAM</option>
            <option value="enterprise">ENTERPRISE</option>
          </select>
          <button
            onClick={startTour}
            className="tour-btn"
          >
            [INIT_TOUR]
          </button>
        </div>

        {/* Retro Product Tour Component */}
        <ProductTourRetro
          isEnabled={isTourEnabled}
          onExit={stopTour}
          userType={userType}
        />

        {/* Retro Styling */}
        <style jsx>{`
          .retro-aios-container {
            min-height: 100vh;
            background: linear-gradient(135deg, #0a0a2e 0%, #16213e 50%, #0f3460 100%);
            color: #00ffff;
            font-family: 'Courier Prime', 'Courier New', monospace;
            padding: 0;
            margin: 0;
            overflow-x: hidden;
          }

          .retro-header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid #00ffff;
          }

          .ascii-title {
            margin-bottom: 20px;
          }

          .title-3d {
            font-size: 8px;
            line-height: 1;
            color: #ffffff;
            text-shadow: 
              1px 1px 0 #ff0000,
              2px 2px 0 #ff8800,
              3px 3px 0 #ffff00,
              4px 4px 0 #00ff00,
              5px 5px 0 #0088ff,
              6px 6px 0 #0000ff,
              7px 7px 0 #8800ff,
              8px 8px 10px rgba(0, 0, 0, 0.5);
            margin: 0;
            font-weight: bold;
          }

          .boot-message {
            color: #00ffff;
            font-size: 14px;
            margin: 20px 0;
            text-transform: uppercase;
            letter-spacing: 2px;
          }

          .retro-nav {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
          }

          .nav-item {
            color: #00ffff;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
          }

          .nav-item.active {
            color: #ffffff;
            text-shadow: 0 0 10px #00ffff;
            border-bottom: 2px solid #00ffff;
            padding-bottom: 2px;
          }

          .nav-item:hover {
            color: #ffffff;
            text-shadow: 0 0 5px #00ffff;
          }

          .rainbow-bar {
            height: 4px;
            background: linear-gradient(90deg, 
              #ff0000 0%, 
              #ff8800 14.28%, 
              #ffff00 28.57%, 
              #00ff00 42.86%, 
              #00ffff 57.14%, 
              #0088ff 71.43%, 
              #0000ff 85.71%, 
              #8800ff 100%);
            margin-top: 20px;
          }

          .dashboard-title {
            color: #00ffff;
            font-size: 24px;
            margin: 30px 0 20px 40px;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: normal;
          }

          .retro-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 0 40px 40px 40px;
            max-width: 1400px;
            margin: 0 auto;
          }

          .retro-panel {
            border: 2px solid #00ffff;
            background: rgba(0, 20, 40, 0.8);
            min-height: 200px;
          }

          .full-width {
            grid-column: 1 / -1;
          }

          .panel-header {
            background: #00ffff;
            color: #000000;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
          }

          .panel-content {
            padding: 20px;
          }

          .status-line, .agent-line {
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
            font-size: 14px;
          }

          .status-label, .agent-name {
            color: #00ffff;
            text-transform: uppercase;
          }

          .status-indicator.ok {
            color: #00ff00;
            font-weight: bold;
          }

          .agent-indicator.ready {
            color: #00ff00;
          }

          .agent-indicator.processing {
            color: #ffff00;
            animation: pulse 1.5s infinite;
          }

          .performance-section {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #004466;
          }

          .perf-title {
            color: #00ffff;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
            font-size: 12px;
          }

          .perf-line {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 12px;
            color: #66ccff;
          }

          .perf-value {
            color: #00ff00;
            font-weight: bold;
          }

          .action-buttons {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
          }

          .action-btn {
            background: #004466;
            border: 2px solid #00ffff;
            color: #00ffff;
            padding: 12px 20px;
            font-family: inherit;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s ease;
            letter-spacing: 1px;
          }

          .action-btn:hover {
            background: #006699;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
            text-shadow: 0 0 5px currentColor;
          }

          .action-btn.run-agent {
            border-color: #00ff00;
            color: #00ff00;
          }

          .action-btn.upload-file {
            border-color: #ffff00;
            color: #ffff00;
          }

          .action-btn.view-logs {
            border-color: #ff8800;
            color: #ff8800;
          }

          .action-btn.open-terminal {
            border-color: #ff00ff;
            color: #ff00ff;
          }

          .command-line {
            margin-bottom: 8px;
            font-size: 14px;
          }

          .prompt {
            color: #00ff00;
            margin-right: 8px;
          }

          .command {
            color: #00ffff;
          }

          .command-result {
            margin-bottom: 15px;
            margin-left: 20px;
            font-size: 13px;
          }

          .command-result.completed {
            color: #00ff00;
          }

          .command-result.processing {
            color: #ffff00;
            animation: pulse 1.5s infinite;
          }

          .tour-controls {
            position: fixed;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
          }

          .retro-select {
            background: #001122;
            border: 2px solid #00ffff;
            color: #00ffff;
            padding: 8px 12px;
            font-family: inherit;
            font-size: 12px;
            text-transform: uppercase;
          }

          .tour-btn {
            background: #004466;
            border: 2px solid #00ffff;
            color: #00ffff;
            padding: 8px 16px;
            font-family: inherit;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s ease;
          }

          .tour-btn:hover {
            background: #006699;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
          }

          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }

          /* Responsive Design */
          @media (max-width: 768px) {
            .title-3d {
              font-size: 4px;
            }
            
            .retro-grid {
              grid-template-columns: 1fr;
              padding: 0 20px 20px 20px;
            }
            
            .retro-nav {
              gap: 15px;
            }
            
            .nav-item {
              font-size: 10px;
            }
            
            .dashboard-title {
              margin-left: 20px;
              font-size: 20px;
            }
          }
        `}</style>
      </div>
    </>
  );
};

export default OnboardingDemoRetro; 
import React, { useEffect, useState } from 'react';
import { Steps } from 'intro.js-react';
import 'intro.js/introjs.css';

interface ProductTourRetroProps {
  isEnabled: boolean;
  onExit: () => void;
  userType?: 'individual' | 'team' | 'enterprise';
}

const ProductTourRetro: React.FC<ProductTourRetroProps> = ({ isEnabled, onExit, userType = 'individual' }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const baseSteps = [
    {
      element: '.system-dashboard',
      intro: `
        <div class="retro-tour-step">
          <h3>🚀 WELCOME TO AIOS v2</h3>
          <p>INITIALIZING GUIDED SYSTEM WALKTHROUGH...</p>
          <div class="retro-stats">
            <span>[DURATION: 2 MIN]</span>
            <span>[FEATURES: 5]</span>
            <span>[STATUS: READY]</span>
          </div>
        </div>
      `,
      position: 'auto'
    },
    {
      element: '.quick-actions',
      intro: `
        <div class="retro-tour-step">
          <h3>📁 UPLOAD FILE INTERFACE</h3>
          <p>PRIMARY DOCUMENT PROCESSING GATEWAY. SUPPORTS ALL MAJOR FORMATS WITH QUANTUM-SPEED ANALYSIS.</p>
          <div class="retro-demo">
            <div class="demo-sequence">
              <span class="demo-file">[DOCUMENT.PDF]</span>
              <span class="demo-arrow">→</span>
              <span class="demo-result">[ANALYZED]</span>
            </div>
          </div>
        </div>
      `,
      position: 'bottom'
    },
    {
      element: '.agent-status',
      intro: `
        <div class="retro-tour-step">
          <h3>🤖 AI AGENT NETWORK</h3>
          <p>SPECIALIZED PROCESSING UNITS WORKING IN PARALLEL. EACH AGENT HANDLES SPECIFIC ANALYSIS TASKS.</p>
          <div class="retro-agents">
            <div class="agent-chip">[CONTENTMIND]</div>
            <div class="agent-chip">[CONTEXTMIND]</div>
            <div class="agent-chip">[DIGESTAGENT]</div>
          </div>
        </div>
      `,
      position: 'right'
    },
    {
      element: '.system-status',
      intro: `
        <div class="retro-tour-step">
          <h3>⚡ SYSTEM MONITORING</h3>
          <p>REAL-TIME STATUS OF ALL SYSTEM COMPONENTS. MONITOR PROCESSING QUEUES AND PERFORMANCE METRICS.</p>
          <div class="retro-progress">
            <div class="progress-display">
              <div class="progress-rainbow" style="width: 85%"></div>
            </div>
            <span>[SYSTEM OPTIMAL - ALL SERVICES ONLINE]</span>
          </div>
        </div>
      `,
      position: 'top'
    },
    {
      element: '.command-history',
      intro: `
        <div class="retro-tour-step">
          <h3>📊 COMMAND HISTORY</h3>
          <p>COMPLETE LOG OF ALL PROCESSING OPERATIONS. TRACK DOCUMENT ANALYSIS, AGENT ACTIVITIES, AND RESULTS.</p>
          <div class="retro-features">
            <span>[EXPORT LOGS]</span>
            <span>[SHARE RESULTS]</span>
            <span>[VIEW ANALYTICS]</span>
          </div>
        </div>
      `,
      position: 'top'
    }
  ];

  const teamSteps = [
    ...baseSteps,
    {
      element: '.team-network',
      intro: `
        <div class="retro-tour-step">
          <h3>👥 TEAM NETWORK</h3>
          <p>COLLABORATIVE WORKSPACE FOR MULTI-USER OPERATIONS. REAL-TIME SYNCHRONIZATION AND SHARED PROCESSING QUEUES.</p>
          <div class="retro-collaboration">
            <div class="collab-feature">[LIVE SYNC]</div>
            <div class="collab-feature">[NOTIFICATIONS]</div>
            <div class="collab-feature">[TASK QUEUE]</div>
          </div>
        </div>
      `,
      position: 'right'
    }
  ];

  const enterpriseSteps = [
    ...teamSteps,
    {
      element: '.admin-console',
      intro: `
        <div class="retro-tour-step">
          <h3>🏢 ENTERPRISE CONTROL</h3>
          <p>ADVANCED ADMINISTRATIVE INTERFACE. SECURITY PROTOCOLS, USER MANAGEMENT, AND SYSTEM CONFIGURATION.</p>
          <div class="retro-enterprise">
            <div class="enterprise-feature">[SECURITY CENTER]</div>
            <div class="enterprise-feature">[USER MANAGEMENT]</div>
            <div class="enterprise-feature">[SYSTEM CONFIG]</div>
          </div>
        </div>
      `,
      position: 'left'
    }
  ];

  const getStepsForUserType = () => {
    switch (userType) {
      case 'team':
        return teamSteps;
      case 'enterprise':
        return enterpriseSteps;
      default:
        return baseSteps;
    }
  };

  const finalStep = {
    element: '.upload-file-btn',
    intro: `
      <div class="retro-tour-step retro-final">
        <h3>🚀 SYSTEM READY</h3>
        <p>AIOS v2 INITIALIZATION COMPLETE. ALL SYSTEMS OPERATIONAL AND READY FOR DOCUMENT PROCESSING.</p>
        <div class="retro-encouragement">
          <p><strong>[PRO TIP]</strong> START WITH PDF OR DOCX FILES FOR OPTIMAL RESULTS</p>
          <div class="retro-support">
            <span>[HELP] ACCESS KNOWLEDGE BASE</span>
            <span>[SUPPORT] CONTACT TECHNICAL TEAM</span>
          </div>
        </div>
      </div>
    `,
    position: 'top'
  };

  const allSteps = [...getStepsForUserType(), finalStep];

  const showCompletionCelebration = () => {
    const celebration = document.createElement('div');
    celebration.className = 'retro-celebration';
    celebration.innerHTML = `
      <div class="celebration-content">
        <div class="celebration-ascii">
          <pre>
    ██████╗ ███████╗ █████╗ ██████╗ ██╗   ██╗
    ██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗ ██╔╝
    ██████╔╝█████╗  ███████║██║  ██║ ╚████╔╝ 
    ██╔══██╗██╔══╝  ██╔══██║██║  ██║  ╚██╔╝  
    ██║  ██║███████╗██║  ██║██████╔╝   ██║   
    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝    ╚═╝   
          </pre>
        </div>
        <h2>SYSTEM WALKTHROUGH COMPLETE</h2>
        <p>AIOS v2 READY FOR OPERATION</p>
      </div>
    `;
    document.body.appendChild(celebration);

    setTimeout(() => {
      if (document.body.contains(celebration)) {
        document.body.removeChild(celebration);
      }
    }, 3000);
  };

  // Debug logging
  useEffect(() => {
    console.log('🕹️ RetroTour component rendered:', { isEnabled, userType, stepCount: allSteps.length });
    if (isEnabled) {
      console.log('✨ Retro tour should start now with', allSteps.length, 'steps');
      console.log('First step targets:', allSteps[0]?.element);
    }
  }, [isEnabled, userType, allSteps.length]);

  useEffect(() => {
    const style = document.createElement('style');
    style.id = 'retro-tour-styles';
    style.textContent = `
      /* Retro AIOS Tour Styling */
      .introjs-overlay {
        background: rgba(0, 20, 40, 0.9) !important;
        z-index: 999999 !important;
      }

      .introjs-tooltip {
        background: linear-gradient(135deg, #001122 0%, #002244 100%) !important;
        border-radius: 0 !important;
        border: 2px solid #00ffff !important;
        box-shadow: 
          0 0 20px rgba(0, 255, 255, 0.3),
          inset 0 0 20px rgba(0, 255, 255, 0.1) !important;
        font-family: 'Courier Prime', 'Courier New', monospace !important;
        max-width: 450px !important;
        min-width: 350px !important;
        z-index: 1000000 !important;
      }

      .introjs-tooltip .introjs-tooltiptext {
        padding: 24px !important;
        color: #00ffff !important;
        line-height: 1.6 !important;
        font-size: 14px !important;
        text-shadow: 0 0 5px currentColor !important;
      }

      .introjs-tooltip .introjs-tooltipbuttons {
        padding: 0 24px 24px 24px !important;
        border-top: 1px solid #00ffff !important;
        margin-top: 16px !important;
        padding-top: 20px !important;
      }

      .retro-tour-step h3 {
        margin: 0 0 16px 0 !important;
        color: #00ffff !important;
        font-size: 16px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        text-shadow: 0 0 10px currentColor !important;
      }

      .retro-tour-step p {
        margin: 0 0 20px 0 !important;
        color: #66ccff !important;
        font-size: 13px !important;
        line-height: 1.5 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
      }

      .retro-stats, .retro-features, .retro-collaboration, .retro-enterprise {
        display: flex !important;
        gap: 8px !important;
        flex-wrap: wrap !important;
        margin-top: 16px !important;
      }

      .retro-stats span, .retro-features span, .retro-collaboration div, .retro-enterprise div {
        background: rgba(0, 255, 255, 0.1) !important;
        border: 1px solid #00ffff !important;
        padding: 4px 8px !important;
        font-size: 10px !important;
        color: #00ffff !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
      }

      .retro-demo {
        margin-top: 16px !important;
        padding: 16px !important;
        background: rgba(0, 255, 255, 0.05) !important;
        border: 1px solid #004466 !important;
      }

      .demo-sequence {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 12px !important;
      }

      .demo-file {
        background: rgba(0, 100, 255, 0.2) !important;
        color: #0066ff !important;
        padding: 6px 12px !important;
        font-size: 11px !important;
        font-weight: bold !important;
        border: 1px solid #0066ff !important;
      }

      .demo-arrow {
        color: #00ff00 !important;
        font-weight: bold !important;
        font-size: 16px !important;
        text-shadow: 0 0 5px currentColor !important;
      }

      .demo-result {
        background: rgba(0, 255, 0, 0.2) !important;
        color: #00ff00 !important;
        padding: 6px 12px !important;
        font-size: 11px !important;
        font-weight: bold !important;
        border: 1px solid #00ff00 !important;
      }

      .retro-agents {
        display: flex !important;
        gap: 8px !important;
        margin-top: 16px !important;
        flex-wrap: wrap !important;
      }

      .agent-chip {
        background: rgba(255, 0, 255, 0.1) !important;
        color: #ff00ff !important;
        padding: 4px 8px !important;
        font-size: 10px !important;
        font-weight: bold !important;
        border: 1px solid #ff00ff !important;
        text-transform: uppercase !important;
      }

      .retro-progress {
        margin-top: 16px !important;
      }

      .progress-display {
        width: 100% !important;
        height: 8px !important;
        background: #001122 !important;
        border: 1px solid #00ffff !important;
        margin-bottom: 8px !important;
        position: relative !important;
        overflow: hidden !important;
      }

      .progress-rainbow {
        height: 100% !important;
        background: linear-gradient(90deg, 
          #ff0000 0%, 
          #ff8800 16.66%, 
          #ffff00 33.33%, 
          #00ff00 50%, 
          #0088ff 66.66%, 
          #0000ff 83.33%, 
          #8800ff 100%) !important;
        transition: width 0.3s ease !important;
      }

      .retro-final {
        text-align: center !important;
      }

      .retro-encouragement {
        background: rgba(0, 255, 255, 0.05) !important;
        padding: 16px !important;
        border: 1px solid #004466 !important;
        margin-top: 16px !important;
      }

      .retro-encouragement p {
        margin: 0 0 12px 0 !important;
        color: #00ffff !important;
        font-weight: bold !important;
      }

      .retro-support {
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
      }

      .retro-support span {
        font-size: 10px !important;
        color: #66ccff !important;
        text-transform: uppercase !important;
      }

      .introjs-helperLayer {
        border: 2px solid #00ffff !important;
        box-shadow: 
          0 0 20px rgba(0, 255, 255, 0.5),
          inset 0 0 20px rgba(0, 255, 255, 0.1) !important;
        position: relative !important;
        z-index: 999998 !important;
      }

      .introjs-button {
        background: linear-gradient(135deg, #004466 0%, #006699 100%) !important;
        border: 2px solid #00ffff !important;
        color: #00ffff !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        font-family: inherit !important;
        text-shadow: 0 0 5px currentColor !important;
      }

      .introjs-button:hover {
        background: linear-gradient(135deg, #006699 0%, #0088cc 100%) !important;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.5) !important;
        text-shadow: 0 0 10px currentColor !important;
      }

      .introjs-skipbutton {
        background: transparent !important;
        color: #66ccff !important;
        border: 2px solid #66ccff !important;
        padding: 8px 16px !important;
        font-weight: bold !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-size: 12px !important;
        font-family: inherit !important;
        text-transform: uppercase !important;
      }

      .introjs-skipbutton:hover {
        background: rgba(102, 204, 255, 0.1) !important;
        color: #00ffff !important;
        border-color: #00ffff !important;
      }

      .retro-celebration {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        background: rgba(0, 20, 40, 0.95) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        z-index: 10000 !important;
        animation: fadeIn 0.3s ease !important;
      }

      .celebration-content {
        background: linear-gradient(135deg, #001122 0%, #002244 100%) !important;
        padding: 40px !important;
        border: 2px solid #00ffff !important;
        text-align: center !important;
        animation: slideInUp 0.5s ease !important;
        box-shadow: 
          0 0 30px rgba(0, 255, 255, 0.5),
          inset 0 0 30px rgba(0, 255, 255, 0.1) !important;
      }

      .celebration-ascii {
        color: #00ffff !important;
        font-size: 8px !important;
        margin-bottom: 20px !important;
        text-shadow: 0 0 10px currentColor !important;
        animation: glow 2s ease-in-out infinite alternate !important;
      }

      .celebration-content h2 {
        margin: 0 0 16px 0 !important;
        color: #00ffff !important;
        font-size: 18px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        text-shadow: 0 0 10px currentColor !important;
      }

      .celebration-content p {
        margin: 0 !important;
        color: #66ccff !important;
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
      }

      @keyframes fadeIn {
        from { opacity: 0 !important; }
        to { opacity: 1 !important; }
      }

      @keyframes slideInUp {
        from { 
          opacity: 0 !important;
          transform: translateY(50px) !important;
        }
        to { 
          opacity: 1 !important;
          transform: translateY(0) !important;
        }
      }

      @keyframes glow {
        from { 
          text-shadow: 0 0 10px #00ffff !important;
        }
        to { 
          text-shadow: 0 0 20px #00ffff, 0 0 30px #00ffff !important;
        }
      }
    `;
    document.head.appendChild(style);

    return () => {
      const existingStyle = document.getElementById('retro-tour-styles');
      if (existingStyle && document.head.contains(existingStyle)) {
        document.head.removeChild(existingStyle);
      }
    };
  }, []);

  return (
    <Steps
      enabled={isEnabled}
      steps={allSteps}
      initialStep={0}
      onExit={onExit}
      onComplete={() => {
        console.log('Retro tour completed');
        onExit();
        showCompletionCelebration();
      }}
      onStepChange={(stepIndex: number) => {
        setCurrentStep(stepIndex);
        console.log(`Retro tour step ${stepIndex + 1} of ${allSteps.length}`);
      }}
      options={{
        tooltipClass: 'introjs-tooltip',
        highlightClass: 'introjs-helperLayer',
        exitOnEsc: true,
        exitOnOverlayClick: false,
        showStepNumbers: true,
        keyboardNavigation: true,
        showButtons: true,
        showBullets: false,
        showProgress: true,
        scrollToElement: true,
        overlayOpacity: 0.9,
        disableInteraction: false,
        nextLabel: '[NEXT]',
        prevLabel: '[BACK]',
        skipLabel: '[SKIP]',
        doneLabel: '[COMPLETE]'
      }}
    />
  );
};

export default ProductTourRetro; 
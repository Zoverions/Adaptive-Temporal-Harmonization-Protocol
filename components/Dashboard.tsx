
import React from 'react';
import { SYNC_ARCHITECTURE, SPOOFING_MITIGATION, COGNITIVE_PRINCIPLES } from '../constants';
import ProtocolCard from './ProtocolCard';
import SyncVisualization from './SyncVisualization';
import SectionTitle from './SectionTitle';
import PilotInterface from './Pilot/PilotInterface';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-12">

      {/* Live Pilot Interface */}
      <section>
        <PilotInterface />
      </section>
      
      {/* Synchronization Architecture Section */}
      <section>
        <SectionTitle title="Synchronization Architecture" subtitle="Technical Implementation" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <SyncVisualization />
          <div className="space-y-6">
            {SYNC_ARCHITECTURE.map((step) => (
              <div key={step.title} className="bg-slate-800/50 p-4 rounded-lg border border-slate-700 hover:border-cyan-400 transition-colors duration-300">
                <h3 className="font-bold text-cyan-400">{step.title}</h3>
                <p className="text-slate-300 mt-1 text-sm">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Rhythmic Spoofing Mitigation Section */}
      <section>
        <SectionTitle title="Rhythmic Spoofing Mitigation" subtitle="Security Augmentation" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {SPOOFING_MITIGATION.map((protocol) => (
            <ProtocolCard key={protocol.title} protocol={protocol} />
          ))}
        </div>
      </section>

      {/* Cognitive Principle Alignment Section */}
      <section>
        <SectionTitle title="Cognitive Principle Alignment" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {COGNITIVE_PRINCIPLES.map((principle) => (
            <div key={principle.title} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-xl font-semibold text-violet-400 mb-2">{principle.title}</h3>
              <p className="text-slate-300">{principle.description}</p>
            </div>
          ))}
        </div>
      </section>
      
    </div>
  );
};

export default Dashboard;

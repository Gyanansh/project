import { useEffect, useState } from 'react';
import { getReport, getRoadmap } from '../services/api';
import { Map, Database, Server } from 'lucide-react';

const ReportView = ({ owner, repo }) => {
    const [report, setReport] = useState(null);
    const [roadmap, setRoadmap] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [reportData, roadmapData] = await Promise.all([
                    getReport(owner, repo),
                    getRoadmap(owner, repo)
                ]);
                setReport(reportData);
                setRoadmap(roadmapData);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [owner, repo]);

    if (loading) return <div className="p-8 text-center text-slate-400">Generating Report & Roadmap...</div>;

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <h1 className="text-3xl font-bold text-slate-900">Project Analysis & Roadmap</h1>

            {/* Architecture Report */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                    <h3 className="font-semibold text-lg mb-4 flex items-center gap-2 text-indigo-600">
                        <Database size={20} /> Database Overview
                    </h3>
                    <p className="text-slate-600 text-sm">{report?.database_overview}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                    <h3 className="font-semibold text-lg mb-4 flex items-center gap-2 text-pink-600">
                        <Server size={20} /> API Overview
                    </h3>
                    <p className="text-slate-600 text-sm">{report?.api_overview}</p>
                </div>
            </div>

            {/* Roadmap */}
            <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500"></div>

                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                    <Map className="text-blue-500" /> Improvement Roadmap
                </h2>

                <div className="space-y-6">
                    {/* Using pre-wrap to handle the raw text from LLM for now. Ideally parsing markdown. */}
                    <div className="prose prose-slate max-w-none">
                        <pre className="whitespace-pre-wrap font-sans text-base leading-relaxed text-slate-700 bg-slate-50 p-6 rounded-lg border border-slate-100">
                            {roadmap?.roadmap}
                        </pre>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReportView;

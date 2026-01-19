import { useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { analyzeFile } from '../services/api';
import { AlertTriangle, Lightbulb, Code as CodeIcon, FileText } from 'lucide-react';

const FileAnalysis = () => {
    const { owner, repo, "*": path } = useParams(); // Catch-all for path
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    const decodedPath = decodeURIComponent(path);

    useEffect(() => {
        const fetchAnalysis = async () => {
            setLoading(true);
            try {
                const result = await analyzeFile(owner, repo, decodedPath);
                setData(result);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalysis();
    }, [owner, repo, decodedPath]);

    if (loading) return (
        <div className="flex items-center justify-center h-64 text-slate-400 gap-2">
            <div className="animate-spin h-5 w-5 border-2 border-blue-500 rounded-full border-t-transparent"></div>
            Analyzing file with AI...
        </div>
    );

    if (!data) return <div className="text-red-500">Failed to load analysis.</div>;

    return (
        <div className="max-w-4xl mx-auto space-y-8 pb-10">
            {/* Header */}
            <div>
                <h2 className="text-2xl font-bold flex items-center gap-2">
                    <FileText className="text-blue-500" />
                    {decodedPath.split('/').pop()}
                </h2>
                <p className="text-slate-500 mt-1">{decodedPath}</p>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-3 gap-4">
                <MetricCard label="Lines of Code" value={data.metrics.lines_of_code} />
                <MetricCard label="Functions" value={data.metrics.function_count} />
                <MetricCard label="Size" value={`${data.metrics.size_bytes} B`} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Analysis Panel */}
                <div className="space-y-6">
                    <Section title="AI Summary" icon={<Lightbulb className="text-yellow-500" />}>
                        <p className="whitespace-pre-wrap text-slate-700 leading-relaxed text-sm">
                            {data.summary}
                        </p>
                    </Section>

                    <Section title="Refactoring Suggestions" icon={<CodeIcon className="text-purple-500" />}>
                        <div className="bg-slate-900 text-slate-200 p-4 rounded-md text-sm overflow-x-auto font-mono">
                            <pre>{data.refactoring_suggestions[0]}</pre>
                        </div>
                    </Section>
                </div>

                {/* Code Panel (Just text for now, could be Monaco Editor) */}
                {/* Actually, user might want to see the code context. 
                     The API returned the analysis, but we might want to show original code too.
                     The backend `analyzeFile` returns analysis result. Wait, did we return content?
                     Check backend `AnalysisResult`. It doesn't have raw content properly.
                     But we can fetch it separately or rely on what we have. 
                     Let's assume the user wants the analysis mostly.
                  */}
                <div>
                    {/* Placeholder for code if needed, or maybe just analysis is enough as requested. */}
                </div>
            </div>
        </div>
    );
};

const Section = ({ title, icon, children }) => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
            {icon} {title}
        </h3>
        {children}
    </div>
);

const MetricCard = ({ label, value }) => (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-100 text-center">
        <div className="text-2xl font-bold text-slate-800">{value}</div>
        <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold">{label}</div>
    </div>
);

export default FileAnalysis;

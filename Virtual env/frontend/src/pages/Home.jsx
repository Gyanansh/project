import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Github, ArrowRight } from 'lucide-react';

const Home = () => {
    const [input, setInput] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        // Parse input (supports "owner/repo" or full URL)
        let owner, repo;
        if (input.includes('github.com')) {
            const parts = input.split('github.com/')[1].split('/');
            owner = parts[0];
            repo = parts[1];
        } else {
            const parts = input.split('/');
            owner = parts[0];
            repo = parts[1];
        }

        if (owner && repo) {
            navigate(`/repo/${owner}/${repo}`);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white px-4">
            <div className="max-w-2xl w-full text-center space-y-8">
                <div className="flex justify-center mb-6">
                    <Github size={64} className="text-blue-400" />
                </div>
                <h1 className="text-5xl font-bold tracking-tight">RepoMaster AI</h1>
                <p className="text-xl text-slate-300">
                    Analyze, understand, and contribute to open source with AI-powered insights.
                </p>

                <form onSubmit={handleSubmit} className="relative max-w-lg mx-auto mt-10">
                    <input
                        type="text"
                        className="w-full px-6 py-4 rounded-full bg-slate-700/50 border border-slate-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 text-lg outline-none placeholder:text-slate-400"
                        placeholder="owner/repo or GitHub URL"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                    />
                    <button
                        type="submit"
                        className="absolute right-2 top-2 bottom-2 bg-blue-600 hover:bg-blue-500 text-white px-6 rounded-full flex items-center gap-2 transition-all font-medium"
                    >
                        Analyze <ArrowRight size={18} />
                    </button>
                </form>

                <div className="pt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                    <FeatureCard title="Tree Visualizer" desc="Interactive file tree exploration." />
                    <FeatureCard title="AI Code Analysis" desc="Deep explanations & refactoring." />
                    <FeatureCard title="Contribution Roadmap" desc="Guided path to your first PR." />
                </div>
            </div>
        </div>
    );
};

const FeatureCard = ({ title, desc }) => (
    <div className="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition">
        <h3 className="font-semibold text-lg mb-1 text-blue-300">{title}</h3>
        <p className="text-sm text-slate-400">{desc}</p>
    </div>
);

export default Home;

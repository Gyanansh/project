import { useEffect, useState } from 'react';
import { getContributionGuide } from '../services/api';
import { BookOpen } from 'lucide-react';

const ContributionGuide = ({ owner, repo }) => {
    const [guide, setGuide] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchGuide = async () => {
            setLoading(true);
            try {
                const data = await getContributionGuide(owner, repo);
                setGuide(data.guide);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        fetchGuide();
    }, [owner, repo]);

    if (loading) return <div className="p-8 text-center text-slate-400">Loading contribution guide...</div>;

    return (
        <div className="max-w-3xl mx-auto">
            <div className="flex items-center gap-3 mb-8">
                <div className="p-3 bg-green-100 text-green-600 rounded-lg">
                    <BookOpen size={24} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Contribution Guide</h1>
                    <p className="text-slate-500">How to contribute to {owner}/{repo}</p>
                </div>
            </div>

            <div className="prose prose-slate max-w-none bg-white p-8 rounded-xl shadow-sm border border-slate-200">
                <pre className="whitespace-pre-wrap font-sans text-base">{guide}</pre>
            </div>
        </div>
    );
};

export default ContributionGuide;

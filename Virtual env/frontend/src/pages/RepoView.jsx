import { useEffect, useState } from 'react';
import { useParams, Routes, Route, Link, useLocation } from 'react-router-dom';
import { getRepoTree } from '../services/api';
import TreeView from '../components/TreeView';
import FileAnalysis from '../components/FileAnalysis';
import ReportView from '../components/ReportView';
import ContributionGuide from '../components/ContributionGuide';
import { FileText, Map, BookOpen, GitPullRequest } from 'lucide-react';

const RepoView = () => {
    const { owner, repo } = useParams();
    const [tree, setTree] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTree = async () => {
            try {
                const data = await getRepoTree(owner, repo);
                setTree(data.tree);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        fetchTree();
    }, [owner, repo]);

    return (
        <div className="flex h-screen overflow-hidden bg-white">
            {/* Sidebar - Tree */}
            <div className="w-80 bg-slate-50 border-r border-slate-200 flex flex-col">
                <div className="p-4 border-b border-slate-200 bg-white">
                    <h2 className="font-bold text-lg truncate" title={`${owner}/${repo}`}>{owner}/{repo}</h2>
                    <div className="flex gap-2 mt-4 text-sm font-medium">
                        <Link to={`/repo/${owner}/${repo}/report`} className="flex-1 py-1.5 px-2 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 flex items-center justify-center gap-1">
                            <Map size={14} /> Roadmap
                        </Link>
                        <Link to={`/repo/${owner}/${repo}/guide`} className="flex-1 py-1.5 px-2 bg-green-50 text-green-700 rounded hover:bg-green-100 flex items-center justify-center gap-1">
                            <BookOpen size={14} /> Guide
                        </Link>
                    </div>
                </div>
                <div className="flex-1 overflow-y-auto p-2">
                    {loading ? (
                        <div className="text-center p-4 text-slate-400">Loading tree...</div>
                    ) : (
                        <TreeView tree={tree} owner={owner} repo={repo} />
                    )}
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-white shadow-sm z-10">
                    <div className="font-medium text-slate-600">
                        {/* Breadcrumbs could go here */}
                        RepoMaster AI Analysis
                    </div>
                    <Link to="/" className="text-sm text-slate-400 hover:text-slate-600">Change Repo</Link>
                </div>

                <div className="flex-1 overflow-y-auto bg-slate-50 p-6 scroll-smooth">
                    <Routes>
                        <Route path="blob/*" element={<FileAnalysis />} />
                        <Route path="report" element={<ReportView owner={owner} repo={repo} />} />
                        <Route path="guide" element={<ContributionGuide owner={owner} repo={repo} />} />
                        <Route path="*" element={
                            <div className="flex flex-col items-center justify-center h-full text-slate-400">
                                <FileText size={48} className="mb-4 opacity-50" />
                                <p>Select a file to analyze or view the Roadmap.</p>
                            </div>
                        } />
                    </Routes>
                </div>
            </div>
        </div>
    );
};

export default RepoView;

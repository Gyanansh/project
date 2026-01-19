import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Folder, FolderOpen, FileCode, ChevronRight, ChevronDown } from 'lucide-react';

// Helper to organize flat list into nested structure
const buildTree = (files) => {
    const root = {};
    files.forEach(file => {
        const parts = file.path.split('/');
        let current = root;
        parts.forEach((part, i) => {
            if (!current[part]) {
                current[part] = {
                    name: part,
                    path: file.path,
                    type: i === parts.length - 1 && file.type === 'blob' ? 'file' : 'folder',
                    children: {}
                };
            }
            current = current[part].children;
        });
    });
    return root;
};

const TreeNode = ({ node, owner, repo }) => {
    const [isOpen, setIsOpen] = useState(false);
    const hasChildren = Object.keys(node.children).length > 0;
    const navigate = useNavigate();

    const handleClick = (e) => {
        e.stopPropagation();
        if (node.type === 'folder') {
            setIsOpen(!isOpen);
        } else {
            // Navigate to file view
            // encode path to handle slashes in filenames if any, though usually path is full path
            // But we need to pass full path to analyze
            // We can use a query param or encode URI component
            navigate(`/repo/${owner}/${repo}/blob/${encodeURIComponent(node.path)}`);
        }
    };

    return (
        <div className="pl-3">
            <div
                className={`flex items-center gap-1.5 py-1 px-2 rounded cursor-pointer hover:bg-slate-100 transition text-sm ${node.type === 'file' ? 'text-slate-600' : 'text-slate-800 font-medium'}`}
                onClick={handleClick}
            >
                {node.type === 'folder' ? (
                    <span className="opacity-50 text-xs">{isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}</span>
                ) : <span className="w-[14px]"></span>}

                {node.type === 'folder' ? (
                    isOpen ? <FolderOpen size={16} className="text-blue-400" /> : <Folder size={16} className="text-blue-400" />
                ) : (
                    <FileCode size={16} className="text-slate-400" />
                )}

                <span className="truncate">{node.name}</span>
            </div>
            {isOpen && hasChildren && (
                <div className="border-l border-slate-200 ml-2">
                    {Object.values(node.children).map((child) => (
                        <TreeNode key={child.path} node={child} owner={owner} repo={repo} />
                    ))}
                </div>
            )}
        </div>
    );
};

const TreeView = ({ tree, owner, repo }) => {
    if (!tree) return null;
    const root = buildTree(tree);

    return (
        <div className="select-none">
            {Object.values(root).map((node) => (
                <TreeNode key={node.path} node={node} owner={owner} repo={repo} />
            ))}
        </div>
    );
};

export default TreeView;

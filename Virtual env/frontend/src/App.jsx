import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import RepoView from './pages/RepoView';

function App() {
    return (
        <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/repo/:owner/:repo/*" element={<RepoView />} />
            </Routes>
        </div>
    );
}

export default App;

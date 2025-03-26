import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from './Home';
import EmailProcessor from './EmailProcessor';
import styles from './App.module.css'; // Import the new CSS module

function App() {
  return (
    <Router>
      <div className={styles.appContainer}>
        {/* Navigation */}
        <nav className={styles.navHeader}>
          <ul className={styles.navList}>
            <li>
              <Link to="/" className={styles.navLink}>Home</Link>
            </li>
            <li>
              <Link to="/email-processor" className={styles.navLink}>Email Processor</Link>
            </li>
          </ul>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/email-processor" element={<EmailProcessor />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
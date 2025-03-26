import React, { useState } from 'react';
import axios from 'axios';
import { FaFileUpload, FaDownload, FaExclamationCircle, FaClipboardList, FaSpinner } from 'react-icons/fa';
import styles from './EmailProcessor.module.css';

function EmailProcessor() {
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            console.log('Selected file:', selectedFile.name, selectedFile.type, selectedFile.size);
            setFile(selectedFile);
            setError(null);
        } else {
            console.log('No file selected');
            setError('No file selected.');
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            console.log('Dropped file:', droppedFile.name, droppedFile.type, droppedFile.size);
            setFile(droppedFile);
            setError(null);
        } else {
            console.log('No file dropped');
            setError('No file dropped.');
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        e.stopPropagation();

        if (!file) {
            console.log('No file selected for upload');
            setError('Please select a file to upload.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        console.log('FormData prepared with file:', file.name);

        try {
            setIsLoading(true);
            console.log('Sending request to http://localhost:8000/upload-email/');
            const response = await axios.post('http://localhost:8000/upload-email/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            console.log('Response received:', response.data);
            setResult(response.data);
            setError(null);
        } catch (err) {
            console.error('Error during upload:', err);
            if (err.response) {
                console.log('Server response:', err.response.data);
                setError(`Server error: ${err.response.data.message || err.response.statusText}`);
            } else if (err.request) {
                console.log('No response received:', err.request);
                setError('No response from server. Is the backend running on http://localhost:8000?');
            } else {
                console.log('Error setting up request:', err.message);
                setError(`Error: ${err.message}`);
            }
            setResult(null);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDownload = () => {
        if (result?.service_intake_request) {
            const dataStr = JSON.stringify(result.service_intake_request, null, 2);
            const blob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'service-intake-data.json';
            link.click();
            URL.revokeObjectURL(url);
        }
    };

    const renderValue = (value) => {
        if (Array.isArray(value)) {
            return (
                <ul className={styles.list}>
                    {value.map((item, index) => (
                        <li key={index}>{item}</li>
                    ))}
                </ul>
            );
        } else if (typeof value === 'object' && value !== null) {
            return (
                <div className={styles.nestedData}>
                    {Object.entries(value).map(([subKey, subValue], index) => (
                        <p key={index}>
                            <strong>{subKey}:</strong> {renderValue(subValue)}
                        </p>
                    ))}
                </div>
            );
        }
        return value || 'N/A';
    };

    const renderServiceRequestDetails = (data) => {
        if (!data) return <p className={styles.noData}>No Service Intake Request Data Available</p>;

        // Log the data to inspect its structure (for debugging)
        console.log('Service Intake Request Data:', data);

        // Extract single-row fields using the exact keys from the data
        const singleRowFields = [
            { key: 'Assigned To', value: data['Assigned To'] },
            { key: 'Description', value: data['Description'] },
            { key: 'Priority', value: data['Priority'] },
            { key: 'Request Type', value: data['Request Type'] },
            { key: 'Sub Request Type', value: data['Sub-Request Type'] },
            { key: 'Summary', value: data['Summary'] },
        ];

        // Extract details for two-column layout
        const details = data.Details || data.details || data.additionalDetails || {};
        const detailEntries = Object.entries(details);
        const detailRows = [];
        for (let i = 0; i < detailEntries.length; i += 2) {
            const firstPair = detailEntries[i];
            const secondPair = detailEntries[i + 1] || null;
            detailRows.push({ firstPair, secondPair });
        }

        return (
            <div className={styles.detailsSection}>
                <h3 className={styles.detailsTitle}>
                    <FaClipboardList className={styles.icon} /> Service Intake Request Details
                </h3>

                {/* Single-Row Fields */}
                <div className={styles.singleRowGrid}>
                    {singleRowFields.map((field, index) => (
                        <div key={index} className={styles.singleRowItem}>
                            <span className={styles.detailKey}>{field.key}:</span>
                            <span className={styles.detailValue}>{renderValue(field.value)}</span>
                        </div>
                    ))}
                </div>

                {/* Details Section with Two Attributes per Row */}
                {detailEntries.length > 0 && (
                    <>
                        <h4 className={styles.subSectionTitle}>Details</h4>
                        <div className={styles.detailsGrid}>
                            {detailRows.map((row, rowIndex) => (
                                <div key={rowIndex} className={styles.detailRow}>
                                    <div className={styles.detailItem}>
                                        <span className={styles.detailKey}>{row.firstPair[0]}:</span>
                                        <span className={styles.detailValue}>{renderValue(row.firstPair[1])}</span>
                                    </div>
                                    {row.secondPair && (
                                        <div className={styles.detailItem}>
                                            <span className={styles.detailKey}>{row.secondPair[0]}:</span>
                                            <span className={styles.detailValue}>{renderValue(row.secondPair[1])}</span>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </div>
        );
    };

    return (
        <div className={styles.emailProcessorContainer}>
            <h1 className={styles.title}>Email Processing Engine</h1>

            {/* File Upload Section */}
            <div className={styles.formGroup}>
                <label htmlFor="fileInput" className={styles.label}>
                    Upload Email File (or Drag & Drop):
                </label>
                <div
                    className={styles.dropZone}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                >
                    <input
                        type="file"
                        id="fileInput"
                        accept=".eml,.pdf,.docx"
                        onChange={handleFileChange}
                        className={styles.fileInput}
                    />
                    <p className={styles.dropZoneText}>
                        {file ? file.name : 'Drag a file here or click to upload'}
                    </p>
                </div>
                <button
                    onClick={handleUpload}
                    className={styles.uploadButton}
                    disabled={isLoading}
                >
                    {isLoading ? (
                        <>
                            <FaSpinner className={styles.spinner} /> Processing...
                        </>
                    ) : (
                        <>
                            <FaFileUpload className={styles.icon} /> Process Email
                        </>
                    )}
                </button>
            </div>

            {/* Error Message */}
            {error && (
                <p className={styles.error}>
                    <FaExclamationCircle className={styles.icon} /> {error}
                </p>
            )}

            {/* Service Intake Request Details */}
            {result?.service_intake_request && (
                <div className={styles.resultContainer}>
                    {renderServiceRequestDetails(result.service_intake_request)}
                    <button onClick={handleDownload} className={styles.downloadButton}>
                        <FaDownload className={styles.icon} /> Download Service Intake Data
                    </button>
                </div>
            )}
        </div>
    );
}

export default EmailProcessor;
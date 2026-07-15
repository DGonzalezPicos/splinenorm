import numpy as np
from scipy.optimize import nnls

def solve_linear(d: np.ndarray, 
                     C_inv: np.ndarray, 
                     M: np.ndarray, 
                     use_nnls: bool = True):
        """
        Solve for linear amplitudes of design matrix.
        
        Automatically detects whether C_inv is a 1D or 2D array and uses the 
        appropriate algorithm for efficiency.
        
        Parameters
        ----------
        d : np.ndarray
            Data vector of shape (n,)
        C_inv : np.ndarray
            Either:
            - Inverse covariance matrix of shape (m, n) for full covariance (m<=n)
            - Inverse variance vector of shape (n,) for diagonal covariance
        M : np.ndarray
            Design matrix of shape (k, n)
        use_nnls : bool, optional
            Whether to use non-negative least squares, by default True
            
        Returns
        -------
        np.ndarray
            Linear amplitudes of shape (n_components,)
        """
        
        M = np.nan_to_num(M, nan=0.0) # replace nan with 0.0
        
        # Determine if C_inv is diagonal (1D array) or full matrix (2D array)
        if C_inv.ndim == 1:
            # Diagonal case: C_inv is the inverse variance vector
            inv_var = C_inv
            
            # Compute M.T @ C_inv @ M efficiently using broadcasting
            weighted_M = M * inv_var[np.newaxis, :]  # (n_components, n_wavelengths)
            lhs = weighted_M @ M.T  # (n_components, n_components)
            
            # Compute M.T @ C_inv @ d efficiently
            rhs = weighted_M @ d  # (n_components,)
            
        elif C_inv.ndim == 2:
            # Full matrix case: C_inv is the inverse covariance matrix
            lhs = M.T @ C_inv @ M
            rhs = M.T @ C_inv @ d
            
        else:
            raise ValueError(f"C_inv must be 1D (diagonal) or 2D (full matrix), got {C_inv.ndim}D")
        
        if use_nnls:
            return nnls(lhs, rhs)[0]
        else:
            return np.linalg.solve(lhs, rhs)
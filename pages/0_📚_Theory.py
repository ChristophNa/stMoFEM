import streamlit as st

st.markdown(
r"""
# Part 1: Theory
## Introduction and motivation for the mixed formulation

We will start this tutorial by introducing the idea of the mixed formulation and its difference from the coupled problem formulation:
- In case of the coupled problem, we consider the interplay between two (or more) sub-problems governed by different physical equations and therefore described by two (or more) fields. Examples of coupled problems include thermoelasticity, electroelasticity, fluid-structure interaction and many others. 
- Mixed problem formulation is obtained upon introduction of one (or more) auxiliary variable(s) in a problem governed by one physical process. 

Examples of classical problems permitting (and benefiting from) mixed formulation include, but are not limited to:
- Incompressible elasticity (auxiliary variable: hydrostatic pressure)
- Stokes/Navier-Stokes problem for viscous incompressible flow (auxiliary variable: fluid pressure)
- Convection-Reaction-Diffusion problem (auxiliary variable: flux)
- Mechanical contact problem (auxiliary variable: contact pressure).

There are multiple reasons for using mixed formulation, see [[Boffi, 2013]](#boffi_2013) for more details:
- Presence of constraints in a problem under study (incompressible elasticity/fluid flow, contact problem)
- Importance of new variables appearing in the formulation (accurate computation of stresses in elastic problem and fluxes in diffusion problem)
- Possibility to obtain weaker formulation with less requirements on the regularity of the solution
- Embedded reliable and efficient <em>a posteriori</em> error estimates.

<!-- Note that in this tutorial particular attention will be given to the error estimators naturally emerging within the mixed formulation and permitting easy implementation of adaptive refinement. -->
## Derivation of the mixed weak form

### Coservation law and boundary conditions

<!-- The strong form of the boundary value problem for the Poisson equation reads: -->

$$
\begin{aligned}
-\textrm{div}\:(\mathbf P) = 0 & \quad \textrm{in}\; \Omega \\
\mathbf u - \bar {\mathbf u} = 0 & \quad \textrm{on}\; \Gamma_u, \\
\bar{\mathbf t} - \mathbf P \cdot \mathbf N = 0 & \quad \textrm{on}\; \Gamma_t,
\end{aligned}
$$

where we assume no body forces acting on the domain, $\mathbf P$ represents the first Piola stress, $\mathbf u$ is the spatial displacement, $\bar{\mathbf u}$ is the spacial displacement boundary condition, $\bar{\mathbf t}$ is the applied traction and $\mathbf N$ is the normal tensor to the respective surface.
### Kinematics <a name="rotations"></a>

The stretch tensor $\mathbf{U}$ is symmetric, whereas rotation $\mathbf{r}$ is orthonormal and can be expressed using exponential map, as follows
\begin{equation}
	\begin{split}
    \label{eq:rotation_definition}
		\mathbf{R} = e^{\mathbf{A}} = \exp(\mathbf{A}) =
		\mathbf{1} + 
		\frac{\sin{(\omega)}}{\omega} 
		\mathbf{A}
		+ 
	  \frac{2\sin^2(\omega/2)}{\omega^2}\mathbf{A}^2 
	\end{split}
\end{equation}
where using indices notation we have
\begin{equation}
    \label{eq:rotation_definition_index_notation}
	R_{iI} = 
	\delta_{iI} 
	+ 
	\frac{\sin{(\omega)}}{\omega} 
	\varepsilon_{iIJ}\omega_J
	+
	\frac{2\sin^2(\omega/2)}{\omega^2} 
  \varepsilon_{iKJ}
  \varepsilon_{KIL}
	\omega_J \omega_L
\end{equation}
where
\begin{equation}
	\omega = \|{\pmb\omega}\|,
	\quad
	\overline{\pmb\omega}=\frac{\pmb\omega}{\omega},
	\quad
	\mathbf{A} = {\pmb\varepsilon} \cdot \overline{\pmb\omega}
\end{equation}
where $\pmb\varepsilon$ is Levi-Civita tensor.
Depending on what kind or rotations (small / medium / large) we want to include in our formulation, different parts of \eqref{eq:rotation_definition} are included in the rotation $\mathbf R$ definition. For large rotations, all of the terms are included. Medium rotations drop the last term, and small rotations assume that $\sin(\omega) \approx \omega$, see L'Hôpital's rule. 
Finally, variation of spatial rotation can be expressed as follows
\begin{equation}
\label{eq:spatial_rotation}
	\delta R_{iI} = 
	\varepsilon_{KIJ} R_{j K} 
	\delta\omega_J
\end{equation}
### Consistency equation

With the above decomposition at hand, starting with consistency equation, we get
\begin{equation}
	\begin{split}
		\left(
		\delta P_{iJ},
		R_{iI} U_{IJ} 
		\right)_{\Omega_0} -
		\left(
		\delta P_{iJ}, 
		\frac{\partial x_{i}}{\partial X_J}
		\right)_{\Omega_0}
		= 0\\
		\left(
		\delta P_{iJ},
		R_{iI} U_{IJ}  
		-
		\delta_{iJ}
		\right)_{\Omega_0} -
		\left(
		\delta P_{iJ}, 
		\frac{\partial u_i}{\partial X_J}
		\right)_{\Omega_0}
    = 0
	\end{split}
\end{equation}

Applying differentiation
by parts to $\left(
		\delta P_{iJ}, 
		\frac{\partial u_i}{\partial X_J}
		\right)_{\Omega_0}$ we get:
\begin{equation}
\label{eq:consistency}
	\begin{split}
	\left(
  \delta P_{iJ},
  R_{iI} U_{IJ}-\delta_{iJ}
	\right)_{\Omega_0} 
	+
	\left(
	\delta P_{iJ,J}	
	, 
	u_i
	\right)_{\Omega_0} 
	-
	\left(
	N_J
	\delta P_{iJ}, \overline{u}_i
	\right)_{\Gamma_0^u}
  &=0.
  \end{split}
\end{equation}

Notice that the displacement $\bar w$ from \eqref{eq:dirichlet} is now applied in the weak sense, which is typical for the mixed formulation. Traction boundary condition \eqref{eq:neuman} is applied *a priory*.
### Physical equation

The physical/constitutive equations are enforced in integral strong sense as follows:
\begin{equation}
\label{eq:physical}
	\begin{split}
	( R_{iI} \delta R_{IJ},
	P_{iJ} - \hat{P}_{iJ}(\mathbf{R}\mathbf{U})
  )_{\Omega_0} = 0
  \\
	( \delta U_{IJ},
	R_{iI} \left(P_{iJ} - \hat{P}_{iJ}(\mathbf{R}\mathbf{U})\right)
  )_{\Omega_0} = 0
  \\
	( \delta U_{IJ},
	R_{iI} \left(P_{iJ} - R_{iI}\hat{P}_{IJ}(\mathbf{U})\right)
  )_{\Omega_0} = 0
  \\
	( \delta U_{IJ},
	R_{iI} P_{iJ} - \hat{P}_{IJ}(\mathbf{U})
  )_{\Omega_0} = 0
	\end{split}
\end{equation}
Note it is weighted only by bases of stretch tensor $\mathbf U$. 
### Angular momentum equation

Angular momentum is satisfied with taking into consideration \eqref{eq:spatial_rotation} as follows:

\begin{equation}
\label{eq:angular_momentum}
	\begin{split}
	(\delta R_{iI}, P_{iI})_{\Omega_0} = 0\\
	(\varepsilon_{ijJ}\delta{\omega}_J R_{jI}, P_{iI})_{\Omega_0} = 0\\
	(\delta{\omega}_J, \varepsilon_{ijJ} P_{iI} R_{jI})_{\Omega_0} = 0
	\end{split}
\end{equation}
### Linear momentum equation

Finally, linear conservation equation is enforced as follows:
\begin{equation}
\label{eq:linear_momentum}
	(\delta u_i,P_{iJ,J})_{\Omega_0} = 0.
\end{equation}
### Element equations

Combining \eqref{eq:consistency}, \eqref{eq:physical}, \eqref{eq:angular_momentum} and \eqref{eq:linear_momentum} gives:

\begin{equation}
\left\{
\begin{split}
	\left(
  \delta P_{iJ},
  R_{iI}U_{IJ} - \delta_{IJ}
	\right)_{\Omega_0} 
  +
	\left(
	\delta P_{i J,  J}	
	, 
	u_i
	\right)_{\Omega_0} 
	-
	\left(
	N_J
	\delta P_{iJ}, \overline{u}_i
	\right)_{\Gamma^w_0}
  &=0
  \\	
	(\delta U_{I J},
	R_{iJ}
	P_{iI} 
	-  \hat{P}_{IJ} (\mathbf{U}))
  )_{\Omega_0}&=0
  \\
  (\delta{\omega}_J, \varepsilon_{ijJ} P_{iI} R_{jI})_{\Omega_0} &= 0
  \\
	(\delta u_i,P_{i I, I})_{\Omega_0} &= 0.
\end{split}
\right.
\end{equation}
### Spaces

With above equations at hand, we choose approximation spaces as follows
\begin{equation}
\label{eq:spaces_linear}
	\left\{
	\begin{array}{l}
		\delta\mathbf{P}\in U_0^h                                                                
		\subset H^\textrm{div}_0(\Omega_0^h) :=                                             
		\{ \delta\mathbf{P} \in H^\textrm{div}(\Omega_0^h) :                                
		N_{j}\delta P_{ij} = 0\;\textrm{on}\;\Gamma_0^{h,u} \}                      \\
		\tilde{\mathbf{P}} + \mathbf{P}\in U^h :=                                                
		\{ \tilde{\mathbf{P}} + \mathbf{P} : \mathbf{P} \in H^\textrm{div}_0(\Omega_0^h) \} \\
		\mathbf{u}, {\pmb\omega}, \delta\mathbf{u}, \delta{\pmb\omega}                           
		\in C^h \subset L^2(\Omega_0^h)                                                     \\
		\mathbf{U},\delta\mathbf{U} \in S^h \subset                                              
		S:=\{ U_{ij} \in L^2(\Omega_0^h)  : U_{ij} = U_{ij}^T \}                         
	\end{array}
	\right.
\end{equation}

In this paper finite element space for stress is defined as follows
<!-- \begin{equation} H^\textrm{div}(\Omega_0^h) =
\mathcal{P}^k(\mathcal{K})+
\textrm{curl}((\textrm{curl}\tilde{\mathbf{A}}^k(\mathcal{K}))\mathbf{b}_K)
\end{equation}  -->
\begin{equation} H^\textrm{div}(\Omega_0^h) =
	\mathcal{RT}^k(\mathcal{K})+
	\textrm{curl}((\textrm{curl}\tilde{\mathbf{A}}^k(\mathcal{K}))\mathbf{b}_\textrm{K})
	\end{equation}
where $\mathcal{K}$ are non-overlapping tetrahedrons covering
$\Omega_0^h$. $\mathcal{RT}^k(\mathcal{K})$ is space of polynomials of
degree $k$, $\mathbf{b}_K$ is "matrix bubble", and
$\tilde{\mathbf{A}}^k(\mathcal{K})$ is antisymmetric matrix homogenous
polynomials of degree $k$. This space can be considered as an extension
of the Raviart–Thomas element by normal bubble h-div space.

\begin{equation}
	{b_\textrm{K}}_{ij}=
	\sum_{l=0}^2 
	\lambda_{l-3}\lambda_{l-2}\lambda_{l-3}
	\lambda_{l,i}\lambda_{l,j}
\end{equation}
### Approximation of logarithmic stretch <a name="log_stretch"></a>

Symmetric stretch tensor $\mathbf u$ is bounded from bellow. It is bounded in a sense that 
its eigen value cannot be smaller (or equal) than zero. In order to build in
*a priori* that kinematic constrain, one can approximate logarithm of stretch tensor
\begin{equation}
  U_{IJ} = \textrm{Exp}(\mathbf{B})_{IJ}
\end{equation}

where $\mathbf B$ is a logarithm of the stretch $\mathbf u$, which corresponds to Hencky strain in this case. 
Therefore:
\begin{equation}
  U_{IJ} = \textrm{Exp}(\mathbf{H})_{IJ}
\end{equation}
Variance of the stretch is therefore

\begin{equation}
\label{eq:variance_stretch_log}
  \delta U_{IJ} = \textrm{Exp}(\mathbf{H})_{IJ,KL} 
  \delta H_{KL}
\end{equation}

With \eqref{eq:variance_stretch_log} at hand, virtual work is 
\begin{equation}
\label{eq:wirtual_work_B}
  \begin{split}
  (\delta U_{IJ},
  R_{i J} P_{iJ} - \hat P_{I J}(\mathbf{U})
  )_{\Omega_0} = 0
  \\
  (
  \textrm{Exp}(\mathbf{H})_{IJ,KL} \delta H_{KL},
  R_{i J} P_{iJ} - \hat P_{I J} (\textrm{Exp}(\mathbf{H}))
  )_{\Omega_0} = 0
  \\
  (
  \delta H_{IJ},
  \textrm{Exp}(\mathbf{H})_{IJ,KL}
  (
  R_{i J} P_{iJ} - \hat P_{I J} (\textrm{Exp}(\mathbf{H}))
  )
  )_{\Omega_0} = 0
  \end{split}
\end{equation}
### Element equations with logarithmic stretch

Replacing the physical equation \eqref{eq:physical} with \eqref{eq:wirtual_work_B}, derived with logarithmic stretches above, results in combining \eqref{eq:consistency}, \eqref{eq:wirtual_work_B}, \eqref{eq:angular_momentum} and \eqref{eq:linear_momentum} for:

\begin{equation}
\left\{
\begin{split}
	\left(
  \delta P_{iJ},
  R_{iI}\textrm{Exp}(\mathbf{H})_{IJ} - \delta_{IJ}
	\right)_{\Omega_0} 
  +
	\left(
	\delta P_{i J,  J}	
	, 
	u_i
	\right)_{\Omega_0} 
	-
	\left(
	N_J
	\delta P_{iJ}, \overline{u}_i
	\right)_{\Gamma^w_0}
  &=0
  \\	
	 (
  \delta H_{IJ},
  \textrm{Exp}(\mathbf{H})_{IJ,KL}
  (
  R_{i J} P_{iJ} - \hat P_{I J} (\textrm{Exp}(\mathbf{H}))
  )
  )_{\Omega_0} &= 0
  \\
  (\delta{\omega}_J, \varepsilon_{ijJ} P_{iI} R_{jI})_{\Omega_0} &= 0
  \\
	(\delta u_i,P_{i I, I})_{\Omega_0} &= 0.
\end{split}
\right.
\end{equation}
\end{equation}
### Spaces with logarithmic stretch

The spaces defined in \eqref{eq:spaces_linear} are also updated:

\begin{equation}
	\left\{
	\begin{array}{l}
		\delta\mathbf{P}\in U_0^h                                                                
		\subset H^\textrm{div}_0(\Omega_0^h) :=                                             
		\{ \delta\mathbf{P} \in H^\textrm{div}(\Omega_0^h) :                                
		N_{j}\delta P_{ij} = 0\;\textrm{on}\;\Gamma_0^{h,u} \}                      \\
		\tilde{\mathbf{P}} + \mathbf{P}\in U^h :=                                                
		\{ \tilde{\mathbf{P}} + \mathbf{P} : \mathbf{P} \in H^\textrm{div}_0(\Omega_0^h) \} \\
		\mathbf{u}, {\pmb\omega}, \delta\mathbf{u}, \delta{\pmb\omega}                           
		\in C^h \subset L^2(\Omega_0^h)                                                     \\
		\mathbf{H},\delta\mathbf{H} \in S^h \subset                                              
		S:=\{ H_{ij} \in L^2(\Omega_0^h)  : H_{ij} = H_{ij}^T \}                         
	\end{array}
	\right.
\end{equation}
### References: 

<a id='boffi_2013'></a> 
**[Boffi, 2013]** Boffi D, Brezzi F, Fortin M. Mixed finite element methods and applications, Springer, 2013

<!-- <a id='repin_2008'></a> 
**[Repin, 2008]** Repin SI. A posteriori estimates for partial differential equations, Walter de Gruyter, 2008 -->
"""
    
)
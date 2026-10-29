# Provenance and scope

This research extension was prepared after reviewing the original `Where Does It Hurt?` code archive and dissertation context. The author reports having written the original code and that the professor generated dummy data specifically for the dissertation.

The synthetic experiments in this package generate their own regions and annotations. They do not load or redistribute the professor-provided dummy dataset or the original coordinate/demographic files.

The point/hull benchmark uses convex hulls to approximate the original region abstraction and compares rasterized strict intersection with thresholded annotation-frequency consensus. It is not a direct benchmark of the original Sutherland–Hodgman clipping implementation. A separate mask-level experiment covers irregular and disconnected regions, but uses a different perturbation model.

This is a working research package for supervisor review, not a submission-ready preprint. Before public release, confirm authorship and contributor roles, university/IP conditions, reuse rights for project-derived code, permission for any professor-provided data to be published, reference metadata, and repository requirements. The original coordinate and demographic files are intentionally excluded.

; IPCC/AR6/WGI/Chapter 8 - Stéphane Sénési - sept 2019 - march 2021

; Multi-plot for 1 variables integrated over 6 or 9 basins (2/3 columns * 3 rows)
; Each plot shows, for three scenarios (ssp), the dependency of the variable with variable 'tas'
; It is shown for an ensemble mean, and with an enveloppe defined by two stat values

; Input data is a netcdf file designated by arg 'input_file'
;  - with the two variables, dimensionned as (ssp,basin,stat,period)
;  - and a variable 'tas', dimensionned as (ssp,period)
;
;  - values of index stat should be  : 0->enveloppe_bottom, 1-> mean, , 2-> enveloppe top,
;  - for color shading to comply with AR6 guidelines, ordering of ssp should be ssp585,ssp245,ssp126
; 
; a number of parameters must be set on Ncl command line; they are listed below, with an example of value
; however, some parameters must be tune to the case, especially the ymin and ymax value for each plot,
; as set through parameters yminmax (near line 105)

begin

  print("begin")
  print(figfile)
 ;  input_file="change_rate_basins_data.nc"
 ;  figfile="./fig.png"
 ; title="Rate of change in basin-scale runoff mean "
 ; xtitle="Warming above 1850-1900, from 1900 to 2100"
 ; ytitle="Change in basin-averaged mean of runoff , vs 1850-1900 (%)"+\
 ;             "~Z75~~C~(13 models ensemble mean, 5 and 95 percentiles)"
 ; var="mrro_mean"
 ; name="runoff"
 ; basins=(/"Amazon","Yangtse","Lena","Danube","Mississippi","Niger/)
 ; experiments_labels = (/"SSP5-8.5","SSP2-4.5","SSP1-2.6"/)
 ; xmin=0.0
 ; xmax=5.05
 ; yminmax=(/(/-43,30/),(/-35,40/),(/-10.,65./),(/-30,40/),(/-40,30/),(/-70,150/) /) 

  function one_plot(wks,num,basin,var,name,tas,vars,yminmax,colors)
  local res
      begin
        
        res=True ;
        delete(res)
        res                      = True
        res@gsnDraw              = False        ; do not draw picture
        res@gsnFrame             = False        ; do not advance frame
        
        
        transparency=0.1
        
        panels=(/"a)","b)","c)","d)","e)","f)","g)","h)","i)"/)
        
        res@xyMonoLineColor  = False
        res@xyMonoLineThickness = False
        res@xyLineThicknesses = (/ 2., 5., 2./)
        res@trXMinF           = xmin
        res@trXMaxF           = xmax
        res@trYMinF           = yminmax(0)
        res@trYMaxF           = yminmax(1)
        res@xyMonoMarkLineMode= False
        res@xyMarkLineModes   = (/"Lines","MarkLines","Lines"/)
        res@xyMarker=16
        res@xyMarkerSizeF=0.012
        res@xyMonoDashPattern = True
        res@tiMainString=panels(num)+" "+basin
        res@tiMainJust="TopLeft"
        res@tiMainOffsetYF= -0.03
        res@tiMainOffsetXF= -0.12
                                ;res@gsnTickMarksOn=False
        res@gsnYRefLine =0.
        res@gsnYRefLineDashPattern = 17
        
        p = new(3,graphic)                   
        
        
        do nssp=1,3
          sspc=colors(nssp-1,:)
          sspf=sspc
          sspf(3)=0.1+nssp*0.05
          res@xyLineColor      = sspc
          res@gsnXYFillColors   = (/sspf,sspf/)
          res@xyMarkerColor = sspc
          p(nssp-1)=gsn_csm_xy(wks,tas(nssp-1,:),vars(nssp-1,0:2,:),res)
        end do
        
        overlay(p(0),p(1))
        overlay(p(0),p(2))
        
        return(p(0))
        
      end

   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    in = addfile(input_file,"r")
    if (.not. isvar("type")) then type="png" end if

    if type .eq. "png" then ;image resolution in pixels
     type@wkWidth = 1024
     type@wkHeight = 1024
   else 
     if (type .eq. "pdf") .or. (type .eq. "eps") then ;image resolution in inches
       type@wkPaperWidthF  = 7.08
       type@wkPaperHeightF = 10.
     end if
   end if
   wks = gsn_open_wks(type,figfile)             ; send graphics to PNG file
   
   plot = new(dimsizes(basins),graphic)                         ; create graphic array

   nplot=dimsizes(basins)
   
   ; Define y values range for each plot 
   if ( .not.(isvar("yminmax"))) 
     ;yminmax=(/(/-45,30/),(/-35,40/),(/-10.,65./),(/-30,45/),(/-45,30/),(/-70,160/) /)
     ; Euphrates en 5
     yminmax=(/(/-45,30/),(/-35,40/),(/-10.,65./),(/-30,45/),(/-90,60/),(/-70,160/) ,(/-30,45/),(/-90,60/),(/-70,160/) /)
   end if

   ; Define colors for scenarios according to AR6 guidelines
   ssp126=(/ 30./256., 150./256.,  132./256., 1. /)
   ssp245=(/ 69./256., 118./256.,  191./256., 1. /)
   ssp585=(/ 128./256., 54./256.,  168./256., 1. /)
   sspall=(/ 1.,1.,1.,1. /)
   colors=(/ssp585,ssp245,ssp126,sspall/)
   
   do ib=0 , nplot - 1
     ; read relevant input time series
     timeseries=in->$var$(ssp|:,basin|ib,stat|:,period|:)
     tas=in->tas(ssp|:,period|:)
     plot(ib)=one_plot(wks,ib,basins(ib),var,name,tas,timeseries,yminmax(ib,:),colors)
   end do
   
   
   ; draw panel with white space added
   txres               = True                     ; text mods desired
   txres@txFontHeightF = 0.015                     ; font smaller. default big
   txres@txJust        = "BottomCenter"
   gsn_text_ndc(wks,xtitle,0.5,0.01,txres)
   
   tyres =True
   tyres@txFontHeightF         = 0.015
   tyres@txAngleF              = 90
   tyres@txJust                = "TopCenter"
   if nplot .le. 6 
     gsn_text_ndc(wks, ytitle, 0.15,0.5,tyres)
   else
     gsn_text_ndc(wks, ytitle, 0.01,0.5,tyres)
   end if
   
   
;***********************************************
; legend resources
;***********************************************
   
   lgres                    = True
   
   lgres@vpWidthF           = 0.2                   ; width of legend (NDC)
   lgres@vpHeightF          = 0.05                   ; height of legend (NDC)
   
   lgres@lgTitleString      = ""
   lgres@lgTitleExtentF     = 0.01
   lgres@lgLabelFontHeightF  = 0.035
   lgres@lgAutoManage       = False                 ; Necessary to set font hgt
   
   lgres@lgMonoLineColor    = False
   lgres@lgLineColors       = colors
   lgres@lgMonoItemType     = True 
   lgres@lgItemType         = "Marklines"
   lgres@lgMonoMarkerIndex  = True
   lgres@lgMarkerIndex      = 16
   lgres@lgMarkerSizeF      = 0.006
   lgres@lgMarkerThicknessF = 1.
   lgres@lgLineThicknessF   = 5
   lgres@lgMonoDashIndex =True
   ;lgres@lgItemTypes        = res@xyMarkLineModes   ; line/marker
   ;lgres@lgDashIndexes      = res@xyDashPatterns    ; dash indexes
   ;lgres@lgMarkerIndexes    = res@xyMarkers         ; marker indexes
   lgres@lgMarkerColors     = colors
   lgres@lgLineLabelStrings = experiments_labels                ; 

;
; Draw the legend, indicating the number of items, a label for each
; item, and the X, Y position of the legend in NDC coordinates.
;
   if nplot .le. 6 
     gsn_legend_ndc(wks,3,experiments_labels,0.235,0.732,lgres)
   else
     gsn_legend_ndc(wks,3,experiments_labels,0.42,0.91,lgres)
   end if
   
   res = True
   res@gsnPanelMainString=title
   res@gsnPanelMainFontHeightF=0.020
   res@gsnPanelBottom=0.05
   res@gsnPanelTop=0.95
   ;resP@gsnPanelYWhiteSpacePercent = 2
   ;resP@gsnPanelXWhiteSpacePercent = 2
   if nplot .le. 6 
     gsn_panel(wks,plot,(/3,2/),res)
   else
     gsn_panel(wks,plot,(/3,3/),res)
   end if

   print("OK")
end

